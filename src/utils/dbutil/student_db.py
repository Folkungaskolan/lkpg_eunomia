""" funktioner som hanterar elever i databasen"""
import inspect
from datetime import datetime

from sqlalchemy import and_

from database.models import Student_dbo, Student_old_dbo, StudentCount_dbo
from database.mysql_db import MysqlDb
from settings.enhetsinfo import ALLA_ENHETER
from utils.EunomiaEnums import EnhetsAggregering
from utils.dbutil.expandera_enheter import expandera_enheter
from utils.faktura_utils._3_4_normalize_split import normalize


def copy_student_counts(from_month: int, to_month: int, from_year: int = 2022, to_year: int = 2022) -> None:
    """ copy student counts from student_dbo to student_count_dbo """
    session = MysqlDb().session()
    for student in session.query(StudentCount_dbo).filter(and_(StudentCount_dbo.month == from_month,
                                                               StudentCount_dbo.year == from_year)
                                                          ).all():
        student_count = StudentCount_dbo(month=to_month,
                                         year=to_year,
                                         id_komplement_pa=student.id_komplement_pa,
                                         count=student.count)
        session.add(student_count)
    session.commit()


def calculate_examen_year(klass: str) -> int:
    """ calculate examen year """
    if "22" in klass:
        return 2022 + 3
    if "21" in klass:
        return 2021 + 3
    if "20" in klass:
        return 2020 + 3
    if klass.startswith("4"):
        return 2022 + 3
    if klass.startswith("5"):
        return 2021 + 3
    if klass.startswith("6"):
        return 2020 + 3
    if klass.startswith("7"):
        return 2022 + 3
    if klass.startswith("8"):
        return 2021 + 3
    if klass.startswith("9"):
        return 2020 + 3
    return -1


def update_student_examen_year(verbose: bool = False) -> None:
    """ update student examen year """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()
    students = s.query(Student_dbo).all()
    for student in students:
        student.klass_examen_year = calculate_examen_year(student.klass)
    s.commit()


def find_and_move_old_students() -> None:  # TODO: Move student to old table when the quit
    """ find and move old students """
    s = MysqlDb().session()
    import_dates = s.query(Student_dbo.last_web_import).order_by(Student_dbo.last_web_import.desc()).first()
    all_students = s.query(Student_dbo).all()
    for student in all_students:
        # if student.user_id == "dalhad279":
        #     print("dalhad279")
        if student.last_web_import.year != import_dates[0].year \
                or student.last_web_import.month != import_dates[0].month \
                or student.last_web_import.day != import_dates[0].day:
            print(student.user_id)

            old_student = s.query(Student_old_dbo).filter(Student_old_dbo.user_id == student.user_id).first()
            if old_student is None:
                old_student = Student_old_dbo(user_id=student.user_id,
                                              google_pw=student.google_pw,
                                              eduroam_pw=student.eduroam_pw,
                                              first_name=student.first_name,
                                              last_name=student.last_name,
                                              eduroam_pw_gen_date=student.eduroam_pw_gen_date,
                                              birthday=student.birthday,
                                              klass=student.klass,
                                              skola=student.skola,
                                              last_web_import=student.last_web_import,
                                              webid=student.webid,
                                              klass_examen_year=student.klass_examen_year,
                                              old=datetime.now()
                                              )
                s.add(old_student)
            else:
                old_student.google_pw = student.google_pw,
                old_student.eduroam_pw = student.eduroam_pw,
                old_student.first_name = student.first_name,
                old_student.last_name = student.last_name,
                old_student.eduroam_pw_gen_date = student.eduroam_pw_gen_date,
                old_student.birthday = student.birthday,
                old_student.klass = student.klass,
                old_student.skola = student.skola,
                old_student.last_web_import = student.last_web_import,
                old_student.webid = student.webid,
                old_student.klass_examen_year = student.klass_examen_year,
                old_student.old = datetime.now()
            s.delete(student)  # ta bort den gamla eleven från den aktiva elev listan
            print(F"Deleting {student.user_id:}")
    s.commit()
    print("find_and_move_old_students  Done")


def calc_split_on_student_count(*, year: int, month: int, enheter_to_split_over: list[str] | EnhetsAggregering) -> dict[str:float]:
    """ Generera split på antal elever """
    s = MysqlDb().session()
    expanderad_enheter_to_split_over = expandera_enheter(enheter_to_split_over)
    for enhet in expanderad_enheter_to_split_over:
        if enhet not in ALLA_ENHETER:
            raise ValueError(F"Enhet finns inte i alla enheter, {expanderad_enheter_to_split_over}")

    abs_distribution = {}  # Variabel initiering
    rel_distribution = {}  # Variabel initiering

    # hämta antal elever
    for enhet in expanderad_enheter_to_split_over:
        enhet_student_count = s.query(StudentCount_dbo.count).filter(StudentCount_dbo.id_komplement_pa == enhet,
                                                                     StudentCount_dbo.month == month,
                                                                     StudentCount_dbo.year == year,
                                                                     ).first()
        if enhet_student_count is None:
            # raise ValueError(f"Kunde inte hitta antal elever för enhet: {enhet}")
            abs_distribution[enhet] = 0
        else:
            abs_distribution[enhet] = enhet_student_count[0]
    total = sum(abs_distribution.values())
    for key in abs_distribution.keys():
        rel_distribution[key] = abs_distribution[key] / total
    return normalize(rel_distribution)


def get_student_enhet_info(*, user_id: str) -> str:
    """ Returnerar enheten som eleven är kopplad till """
    s = MysqlDb().session()
    student = s.query(Student_dbo).filter(Student_dbo.user_id == user_id).first()
    print(student)

    return user_id


if __name__ == '__main__':
    pass
    calc_split_on_student_count(year=1900, month=13, enheter_to_split_over=EnhetsAggregering.STL)
    # copy_student_counts(from_month=10, from_year=2022, to_month=1, to_year=2022)
    # copy_student_counts(from_month=10, from_year=2022, to_month=2, to_year=2022)
    # copy_student_counts(from_month=10, from_year=2022, to_month=3, to_year=2022)
    # copy_student_counts(from_month=10, from_year=2022, to_month=4, to_year=2022)
    # copy_student_counts(from_month=10, from_year=2022, to_month=5, to_year=2022)
    # copy_student_counts(from_month=10, from_year=2022, to_month=6, to_year=2022)
    # copy_student_counts(from_month=10, from_year=2022, to_month=7, to_year=2022)
    # copy_student_counts(from_month=10, from_year=2022, to_month=8, to_year=2022)
    # copy_student_counts(from_month=10, from_year=2022, to_month=9, to_year=2022)

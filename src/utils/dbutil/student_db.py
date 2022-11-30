""" funktioner som hanterar elever i databasen"""
from sqlalchemy import and_

from database.models import Student_dbo, Student_old_dbo, StudentCount_dbo
from database.mysql_db import MysqlDb
from settings.enhetsinfo import ID_AKTIVITET, FOLKUNGA_GRU_ENHETER, STLARS_ENHETER, ENHETER_SOM_HAR_CBS, FOLKUNGA_GY_ENHETER


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


def update_student_examen_year() -> None:
    """ update student examen year """
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


def generate_split_on_student_count(year: int, month: int, enheter_to_split_over: set) -> list[str:float]:
    """ Generera split på antal elever """
    s = MysqlDb().session()

    alla_enheter = set(ID_AKTIVITET.keys())
    if enheter_to_split_over is None:
        enheter_to_split_over = alla_enheter
    elif enheter_to_split_over == {"CB"}:
        enheter_to_split_over = ENHETER_SOM_HAR_CBS
    elif enheter_to_split_over == {"F_GY"}:
        enheter_to_split_over = FOLKUNGA_GY_ENHETER
    elif enheter_to_split_over == {"GRU"}:
        enheter_to_split_over = FOLKUNGA_GRU_ENHETER
    elif enheter_to_split_over == {"STL"}:
        enheter_to_split_over = STLARS_ENHETER
    if any([True for enhet in enheter_to_split_over if enhet not in alla_enheter]):  # Kollar att enheterna vi fick finns i alla enheter
        raise ValueError("Enhet finns inte i alla enheter")

    abs_distribution = {}  # Variabel initiering
    rel_distribution = {}  # Variabel initiering

    # hämta antal elever
    for enhet in enheter_to_split_over:
        enhet_student_count = s.query(StudentCount_dbo.count).filter(StudentCount_dbo.id_komplement_pa == enhet,
                                                                     StudentCount_dbo.month == month,
                                                                     StudentCount_dbo.year == year,
                                                                     ).first()
        if enhet_student_count is None:
            raise ValueError(f"Kunde inte hitta antal elever för enhet: {enhet}")
            abs_distribution[enhet] = 0
            continue
        abs_distribution[enhet] = enhet_student_count[0]
    total = sum(abs_distribution.values())
    for key in abs_distribution.keys():
        rel_distribution[key] = abs_distribution[key] / total

    return rel_distribution


if __name__ == '__main__':
    pass
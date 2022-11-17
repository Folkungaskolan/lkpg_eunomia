""" student access to MySQL """
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import Student_dbo, StudentCount_dbo, Student_old_dbo
from database.mysql_db import MysqlDb


def save_student_information_to_db(user_id: str,
                                   first_name: str = None,
                                   last_name: str = None,
                                   klass: str = None,
                                   skola: str = None,
                                   birthday: str = None,
                                   google_pw: str = None,
                                   eduroam_pw: str = None,
                                   session: Session = None,  # used in multi thread processing as they need a db session each to not conflict
                                   webid: str = None) -> (None, Session):
    """ save student information to mysql"""
    if user_id is None:
        raise ValueError("user_id is None")
    if session is None:
        local_session = MysqlDb().session()
    else:
        local_session = session
    student = local_session.query(Student_dbo).filter(Student_dbo.user_id == user_id).first()
    # print(f"Saveing student |{student.user_id}")
    if student is None:
        student = Student_dbo(user_id=user_id)
        student = _add_info_to_student_obj(student_obj=student,
                                           first_name=first_name,
                                           last_name=last_name,
                                           klass=klass,
                                           skola=skola,
                                           birthday=birthday,
                                           eduroam_pw=eduroam_pw,
                                           pw=google_pw,
                                           webid=webid)
        local_session.add(student)
        local_session.commit()
        return local_session
    student = _add_info_to_student_obj(student_obj=student,
                                       first_name=first_name,
                                       last_name=last_name,
                                       klass=klass,
                                       skola=skola,
                                       birthday=birthday,
                                       eduroam_pw=eduroam_pw,
                                       pw=google_pw,
                                       webid=webid)
    local_session.add(student)
    local_session.commit()
    if session is not None:  # for the multi thread processing to keep their processes separate
        return local_session


def _add_info_to_student_obj(student_obj: Student_dbo,
                             first_name: str = None,
                             last_name: str = None,
                             klass: str = None,
                             skola: str = None,
                             birthday: str = None,
                             eduroam_pw: str = None,
                             pw: str = None,
                             webid: str = None) -> Student_dbo:
    """ factor out variable assigments """
    if first_name is not None:
        student_obj.first_name = first_name
    if last_name is not None:
        student_obj.last_name = last_name
    if klass is not None:
        student_obj.klass = klass
    if skola is not None:
        student_obj.skola = skola
    if birthday is not None:
        student_obj.birthday = birthday
    if pw is not None:
        student_obj.pw = pw
    if eduroam_pw is not None:
        student_obj.eduroam_pw = eduroam_pw
        student_obj.eduroam_pw_gen_date = datetime.now()
    if webid is not None:
        student_obj.webid = webid
    student_obj.last_web_import = datetime.now()
    return student_obj


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


if __name__ == '__main__':
    # update_student_examen_year()
    find_and_move_old_students()
    # copy_student_counts(from_month=10, to_month=8)

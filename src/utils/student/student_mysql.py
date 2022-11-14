""" student access to MySQL """
from datetime import datetime

from sqlalchemy.orm import Session

from database.models import Student_dbo
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
        student = add_info_to_student_obj(student_obj=student,
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
    student = add_info_to_student_obj(student_obj=student,
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
    if session is not None: # for the multi thread processing to keep their processes separate
        return local_session


def add_info_to_student_obj(student_obj: Student_dbo,
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
    return student_obj


if __name__ == '__main__':
    pass
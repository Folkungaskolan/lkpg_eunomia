""" student access to MySQL """
import math
from datetime import datetime
from functools import cache

from sqlalchemy import and_, func
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


@cache
def count_student(endast_id_komplement_pa: set[str] = None, month: int = None) -> tuple[dict[str, int], dict[str, float]]:
    """ Räknar elever i respektive klass i databasen och sparar dessa siffror samt returnerar dem
    return raw_total, relative_distribution
    """
    s = MysqlDb().session()
    raw_total = {}
    relative_distribution = {}
    if month == datetime.now().month or month is None:
        slask = []
        klass_sum = s.query(Student_dbo.klass,
                                        Student_dbo.skola,
                                        func.count(Student_dbo.klass).label("sum")
                                        ).group_by(Student_dbo.klass
                                                   ).all()
        for klass_obj in klass_sum:
            # print(klass)
            if "_FOL" in klass_obj.klass:  # FOLKUNGASKOLAN
                if klass_obj.klass.startswith("EK"):  # EK
                    raw_total["655119"] = raw_total.get("655119", 0) + klass_obj.sum
                elif klass_obj.klass.startswith("ES"):  # ES
                    raw_total["655123"] = raw_total.get("655123", 0) + klass_obj.sum
                elif klass_obj.klass.startswith("SA"):  # SA
                    raw_total["655122"] = raw_total.get("655122", 0) + klass_obj.sum
                elif klass_obj.skola in {"Folkungaskolan 5", "Folkungaskolan 6"}:  # 7-9
                    raw_total["656520"] = raw_total.get("656520", 0) + klass_obj.sum
                elif klass_obj.skola in {"Folkungaskolan 4"}:  # 4-6
                    raw_total["656510"] = raw_total.get("656510", 0) + klass_obj.sum
                continue
            elif "_STL" in klass_obj.klass:  # S:t Lars
                if klass_obj.klass.startswith("NA"):  # NA
                    raw_total["654300"] = raw_total.get("654300", 0) + klass_obj.sum
                elif klass_obj.klass.startswith("ES"):  # ES
                    raw_total["654100"] = raw_total.get("654100", 0) + math.ceil(klass_obj.sum / 2)  # TODO Fråga Maria H om detta är ok
                    raw_total["654200"] = raw_total.get("654200", 0) + math.ceil(klass_obj.sum / 2)
                elif klass_obj.klass.startswith("IMA"):  # IMA
                    raw_total["654400"] = raw_total.get("654400", 0) + klass_obj.sum
                continue
            slask.append(klass_obj.klass)  # om ingen tagit hand om klassen så lägger vi den i slasken
        print(F"slask klasser: {slask}")
        for key in raw_total.keys():
            id_count = s.query(StudentCount_dbo).filter(StudentCount_dbo.id_komplement_pa == key,
                                                                    StudentCount_dbo.month == datetime.now().month,
                                                                    StudentCount_dbo.year == datetime.now().year,
                                                                    ).first()
            if id_count is None:
                s.add(StudentCount_dbo(id_komplement_pa=key,
                                                   count=raw_total[key],
                                                   month=datetime.now().month,
                                                   year=datetime.now().year)
                                  )
            else:
                id_count.count = raw_total[key]
                id_count.month = datetime.now().month
                id_count.year = datetime.now().year
            s.commit()
    else:
        old_month_counts = s.query(StudentCount_dbo).filter(StudentCount_dbo.month == month).all()
        print(old_month_counts)
        for id_komplement_pa in old_month_counts:
            raw_total[id_komplement_pa.id_komplement_pa] = id_komplement_pa.count

    if endast_id_komplement_pa is not None:
        for k in list(raw_total.keys()):
            if k not in endast_id_komplement_pa:
                del raw_total[k]

    total = sum(raw_total.values())
    for key in raw_total.keys():
        relative_distribution[key] = raw_total[key] / total

    return raw_total, relative_distribution





if __name__ == '__main__':
    pass
    # update_student_examen_year()
    # find_and_move_old_students()
    # copy_student_counts(from_month=10, to_month=8)

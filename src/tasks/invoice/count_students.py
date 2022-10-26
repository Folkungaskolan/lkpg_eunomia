from functools import cache

from sqlalchemy.sql.elements import and_

from database.models import Student_dbo
from database.mysql_db import init_db


@cache
def count_student_files_in_folder(headless_bool=None) -> dict[str, int]:
    """ räknar antalet json filer i student mappen
    :return: antalet json filer i student mappen
    """
    local_session = init_db()
    skolor = local_session.query(Student_dbo).distinct(Student_dbo.skola).all()
    for skola in skolor:
        klasser = local_session.query(Student_dbo.klass).distinct().all()
        for klass in klasser:
            student_count = local_session.query(Student_dbo).filter(and_(Student_dbo.skola == skola,
                                                                         Student_dbo.klass == klass)
                                                                    ).count()
            print(f"skola|{skola} klass|{klass} student_count|{student_count}")
    # TODO skriv färdigt


if __name__ == "__main__":
    count_student_files_in_folder()

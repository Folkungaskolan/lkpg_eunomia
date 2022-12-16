""" """
import pytest
from sqlalchemy import and_

from database.models import StudentCount_dbo, Student_dbo
from database.mysql_db import MysqlDb


@pytest.fixture
def setup_test1():
    """ testing fixtures """
    print("setup_test1")
    yield "setup_test123"
    print("teardown_test1")


@pytest.fixture(scope="session")
def base_student_account():
    """
    Create a base student account
    """
    s = MysqlDb().session()
    user_id = "abcabc123"
    s.add(Student_dbo(user_id=user_id,
                      first_name="test_firstname_123",
                      last_name = "test_lastname_abc123",
                      google_pw="testpassword",
                      klass = "EK21B_FOL"
                      ))
    s.commit()
    yield  ## go do the test
    student = s.query(Student_dbo).filter(Student_dbo.user_id == user_id).first()
    s.delete(student)
    s.commit()


@pytest.fixture(scope="session")
def base_student_numbers():  # https://www.youtube.com/watch?v=ErS0PPfLFLI
    """ setup base student numbers in database for testing """
    # print("setup_base_student_numbers")
    s = MysqlDb().session()
    s.add(StudentCount_dbo(year=1900, month=13, count=10, id_komplement_pa="655119"))
    s.add(StudentCount_dbo(year=1900, month=13, count=12, id_komplement_pa="655123"))
    s.add(StudentCount_dbo(year=1900, month=13, count=14, id_komplement_pa="655122"))
    s.add(StudentCount_dbo(year=1900, month=13, count=16, id_komplement_pa="656510"))
    s.add(StudentCount_dbo(year=1900, month=13, count=18, id_komplement_pa="656520"))
    s.add(StudentCount_dbo(year=1900, month=13, count=20, id_komplement_pa="656310"))
    s.add(StudentCount_dbo(year=1900, month=13, count=22, id_komplement_pa="655125"))
    s.add(StudentCount_dbo(year=1900, month=13, count=24, id_komplement_pa="654100"))
    s.add(StudentCount_dbo(year=1900, month=13, count=26, id_komplement_pa="654200"))
    s.add(StudentCount_dbo(year=1900, month=13, count=28, id_komplement_pa="654300"))
    s.add(StudentCount_dbo(year=1900, month=13, count=30, id_komplement_pa="654400"))
    s.add(StudentCount_dbo(year=1900, month=13, count=32, id_komplement_pa="654500"))
    s.commit()
    # print("setup_base_student_numbers")
    yield  ## go do the test
    student_counts = s.query(StudentCount_dbo).filter(and_(StudentCount_dbo.year == 1900,
                                                           StudentCount_dbo.month == 13)
                                                      ).all()
    for student_count in student_counts:
        s.delete(student_count)
    s.commit()
    # print("teardown_base_student_numbers complete")


if __name__ == '__main__':
    pass

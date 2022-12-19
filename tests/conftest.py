""" """
import pytest
from sqlalchemy import and_

from Settings_Student_Numbers import TEST_STUDENT_NUMBERS
from database.models import StudentCount_dbo, Student_dbo
from database.mysql_db import MysqlDb

FLOAT_TOLERANCE_IN_TESTS = 0.0001
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
def base_student_numbers() -> None:  # https://www.youtube.com/watch?v=ErS0PPfLFLI
    """ setup base student numbers in database for testing """
    # print("setup_base_student_numbers")
    s = MysqlDb().session()
    for enhet in TEST_STUDENT_NUMBERS:
        s.add(StudentCount_dbo(year=1900, month=13, count=TEST_STUDENT_NUMBERS[enhet], id_komplement_pa=enhet))
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

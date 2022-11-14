""" spelar det roll om jag har en global session eller om jag skapar en ny session för varje request? """
from database.models import FakturaRadSplit_dbo, Staff_dbo
from database.mysql_db import init_db, MysqlDb
from utils.decorators import function_timer


@function_timer
def create_session_for_each():
    """ Skapar en ny session för varje gång vi ska skriva till databasen """
    print("create_session_for_each")
    for i in range(0, 500):
        s = init_db()
        s.add(FakturaRadSplit_dbo(split_id=1,
                                  faktura_year=2022,
                                  faktura_month=13,
                                  avser=f"test {i}",
                                  split_summa=i)
              )
        s.commit()
        s.close()


@function_timer
def reuse_session():
    """ skapar en session för allt  vi ska skriva till databasen """
    print("create_session_for_each")
    s = MysqlDb().session()
    for i in range(0, 500):
        s.add(FakturaRadSplit_dbo(split_id=1,
                                  faktura_year=2022,
                                  faktura_month=13,
                                  avser=f"test {i}",
                                  split_summa=i)
              )
        s.commit()
    s.close()


def testrun_of_singleton_db() -> None:
    """ Funkar detta ? """
    s1 = MysqlDb()
    print(s1.session())
    s2 = MysqlDb()
    print(s2.session())

    s3 = MysqlDb().session()
    print(s3)
    s4 = MysqlDb().session()
    print(s4)


if __name__ == '__main__':
    # create_session_for_each()
    # reuse_session()
    testrun_of_singleton_db()

""" Funktioner som hanterar databas kopplingen """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from database.models import FakturaRad_dbo, Tjf_dbo, Staff_dbo
from utils.creds import get_cred


def init_db(echo: bool = False) -> Session:
    """ skapar databas kopplingen """
    creds = get_cred(account_file_name="mysql_root_local")
    engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/eunomia", echo=echo)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def demo_distinct():
    """ demo av join """
    session = init_db()
    results = session.query(FakturaRad_dbo.tjanst).distinct().all()
    for result in results:
        print(result.tjanst)


def demo_join() -> None:
    """ demo av join https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.join"""
    session = init_db()
    results = session.query(Tjf_dbo, Staff_dbo.aktivitet_char).join(Staff_dbo, Tjf_dbo.pnr12 == Staff_dbo.pnr12) \
        .limit(5).all()
    for result in results:
        print(f"Tjf_dbo{result.Tjf_dbo} Staff_dbo{result.aktivitet_char}")


if __name__ == '__main__':
    pass
    demo_join()

    # print_user("lyadol")
    # from utils.file_utils.staff_db import delete_user
    #
    # delete_user("lyadol2")
    # insert_user(user_id="lyadol2", first_name="Lyam2", last_name="Dolk2", pnr="0000000000")
    # Base.metadata.create_all(engine)

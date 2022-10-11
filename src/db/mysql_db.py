from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from utils.creds import get_cred


def init_db() -> Session:
    """ skapar databas kopplingen """
    creds = get_cred(account_file_name="mysql_root_local")
    engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/eunomia", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


if __name__ == '__main__':
    pass
    # print_user("lyadol")
    delete_user("lyadol2")
    # insert_user(user_id="lyadol2", first_name="Lyam2", last_name="Dolk2", pnr="0000000000")
    # Base.metadata.create_all(engine)

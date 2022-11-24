""" Funktioner som hanterar databas kopplingen """
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from utils.creds import get_cred


def create_db_engine(creds_filename: str = "mysql_root_local", echo: bool = False) -> Engine:
    """ create mysql engine """
    creds = get_cred(account_file_name=creds_filename)
    connection_string = f"mysql://{creds['usr']}:{creds['pw']}@localhost/eunomia"
    # print(f"connection_string|{connection_string}")
    engine = create_engine(connection_string, echo=echo)
    return engine


def init_db(echo: bool = False) -> Session:
    """ skapar databas kopplingen """
    engine: Engine = create_db_engine(echo=echo)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


class MysqlDb:
    """ singleton session to Mysql db """
    __instance = None  # type: Session
    __session = None

    def __new__(cls):
        if (cls.__instance is None):
            cls.__instance = super(MysqlDb, cls).__new__(cls)
        return cls.__instance

    def session(self, echo: bool = False) -> Session:
        """
        get session
        :param echo: echo sql statements
        """
        if (self.__session is None):
            self.__session = init_db(echo=echo)
        return self.__session


if __name__ == '__main__':
    pass

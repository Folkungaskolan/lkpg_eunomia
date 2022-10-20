from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import Session

from utils.creds import get_cred

Base = declarative_base()
db_name = "orm_test"


def init_db(echo: bool = False) -> Session:
    """ skapar databas kopplingen """
    creds = get_cred(account_file_name="mysql_root_local")
    engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/{db_name}", echo=echo)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


class Parent(Base):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=50))
    children = relationship("Child", back_populates="parent")


class Child(Base):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=50))
    parent_id = Column(Integer, ForeignKey("parent.id"))
    parent = relationship("Parent", back_populates="children")


def create_all_tables(echo: bool = False):
    """ create all tables in database. """
    creds = get_cred(account_file_name="mysql_root_local")
    engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/{db_name}", echo=False)
    Base.metadata.create_all(engine)


def drop_all_tables(echo: bool = False):
    """ drop all tables in database. """
    creds = get_cred(account_file_name="mysql_root_local")
    engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/{db_name}", echo=False)
    Base.metadata.drop_all(engine)


if __name__ == '__main__':
    drop_all_tables()
    create_all_tables()
    # session = init_db()
    # session.add(Parent(name="parent1"))
    # session.commit()

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.creds import get_cred

creds = get_cred(account_file_name="mysql_root_local")
engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/eunomia", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Staff(Base):
    """ db model for staff members. """
    __tablename__ = 'staff'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(length=9))
    first_name = Column(String(length=50))
    last_name = Column(String(length=50))
    pnr = Column(String(length=12))

    # def __init__(self, user_id: str = None, first_name: str = "", last_name: str = "", pnr: str = ""):
    #     if user_id is None:
    #         raise ValueError("user_id must be set")

    def __repr__(self):
        return f"Staff(id:{self.id}|user_id='{self.user_id}', first_name='{self.first_name}', last_name='{self.last_name}', pnr='{self.pnr}')"


def insert_user(user_id: str, first_name: str, last_name: str, pnr: str):
    """ Insert a user into the db. """
    staff = Staff(user_id=user_id, first_name=first_name, last_name=last_name, pnr=pnr)
    session.add(staff)
    session.commit()


def update_user(user_id: str, first_name: str, last_name: str, pnr: str):
    """ Update a user in the db. """
    staff = session.query(Staff).filter_by(user_id=user_id).first()
    staff.first_name = first_name
    staff.last_name = last_name
    staff.pnr = pnr
    session.commit()


def print_user(user_id: str):
    """ Print a user from the db. """
    staff = session.query(Staff).filter_by(user_id=user_id).first()
    print(staff)
    print(type(staff))


def delete_user(user_id: str):
    """ Delete a user from the db. """
    staff = session.query(Staff).filter_by(user_id=user_id).first()
    session.delete(staff)
    session.commit()


if __name__ == '__main__':
    pass
    # print_user("lyadol")
    delete_user("lyadol2")
    # insert_user(user_id="lyadol2", first_name="Lyam2", last_name="Dolk2", pnr="0000000000")
    # Base.metadata.create_all(engine)

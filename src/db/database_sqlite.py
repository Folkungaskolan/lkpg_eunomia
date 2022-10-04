""" Data bas filer för via SQLAlchemy för Eunomia faktura hanterings delar av systemet. """
# https://www.youtube.com/watch?v=NuDSWGOcvtg&t=10s

from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class Student(base):
    """
    test som hanterar en fiktiv student databas
    """
    __tablename__ = 'students'
    anv_namn = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __init__(self, anv_namn, first_name, last_name, fullname, password):
        self.anv_namn = anv_namn
        self.first_name = first_name
        self.last_name = last_name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return f"User(name='{self.name}', fullname='{self.fullname}', password='{self.password}')"


if __name__ == '__main__':
    engine = create_engine('sqlite:///sqlite3.db', echo=True)
    base.metadata.create_all(engine)

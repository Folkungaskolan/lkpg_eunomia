# https://www.youtube.com/watch?v=NuDSWGOcvtg&t=10s

from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///db.sqlite3', echo=True)
base = declarative_base()


class Student(base):
    __tablename__ = 'users'
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


base.metadata.create_all(engine)

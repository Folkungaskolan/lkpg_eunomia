from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, SmallInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base

from utils.creds import get_cred

Base = declarative_base()


class Staff_dbo(Base):
    """ db model for staff members. """
    __tablename__ = 'staff'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(length=10))
    first_name = Column(String(length=50))
    last_name = Column(String(length=50))
    full_name = Column(String(length=70))
    telefon = Column(String(length=20))
    u_created_date = Column(DateTime)
    u_changed_date = Column(DateTime)
    titel = Column(String(length=30))
    domain = Column(String(length=50))
    pnr = Column(String(length=12))
    email = Column(String(length=50))

    def __repr__(self):
        return f"Staff(id:{self.id}|user_id='{self.user_id}', first_name='{self.first_name}', last_name='{self.last_name}', pnr='{self.pnr}')"

    def get_as_dict(self) -> dict[str:str]:
        """ get staff as dict. """
        if self.u_created_date is None:
            u_create = ""
        else:
            u_create = self.u_created_date.strftime("%Y-%m-%d %H:%M:%S")
        if self.u_changed_date is None:
            u_change = ""
        else:
            u_change = self.u_changed_date.strftime("%Y-%m-%d %H:%M:%S")

        return {"id": self.id,
                "user_id": self.user_id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "full_name": self.full_name,
                "telefon": self.telefon,
                "u_created": u_create,
                "u_changed": u_change,
                "titel": self.titel,
                "domain": self.domain,
                "pnr": self.pnr,
                "email": self.email}

    def get_birth_year(self) -> int:
        return int(self.pnr[0:4])

    def get_birth_month(self) -> int:
        return int(self.pnr[4:6])

    def get_birth_day(self) -> int:
        return int(self.pnr[6:8])


class tjf_dbo(Base):
    """ db model for tjf. """
    __tablename__ = 'tjf'
    id = Column(Integer, primary_key=True)
    pnr = Column(String(length=12))
    user_id = Column(String(length=6))
    id_komplement_pa = Column(String(length=6))
    year = Column(SmallInteger)
    month = Column(SmallInteger)
    aktivitet_s = Column(String(length=1))
    aktivitet = Column(String(length=50))
    namn = Column(String(length=50))
    yrke = Column(String(length=50))

    jan = Column(Float)
    feb = Column(Float)
    mar = Column(Float)
    apr = Column(Float)
    maj = Column(Float)
    jun = Column(Float)
    jul = Column(Float)
    aug = Column(Float)
    sep = Column(Float)
    okt = Column(Float)
    dec = Column(Float)
    kommentar = Column(String(length=150))
    personalkategori = Column(String(length=50))


class Student_dbo(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(length=9))
    first_name = Column(String(length=50))
    last_name = Column(String(length=50))
    pnr = Column(String(length=12))
    google_pw = Column(String(length=50))
    eduroam_pw = Column(String(length=10))
    eduroam_pw_gen_date = Column(DateTime(timezone=True))
    klass = Column(String(length=50))


class FakturaRad_dbo(Base):
    __tablename__ = 'faktura_rader'
    id = Column(Integer, primary_key=True)
    tjanst = Column(String(length=50))
    kundnummer = Column(Integer)
    fakturamarkning = Column(String(length=50))
    fakturakod = Column(String(length=50))
    anvandare = Column(String(length=50))
    avser = Column(String(length=50))
    period = Column(String(length=6))
    antal = Column(Integer)
    pris = Column(Float)
    Summa = Column(Float)  # fakturans summans rad
    split_done = Column(Boolean)  # Has row been split into sub sums?
    split_654_e = Column(Float)
    split_655_e = Column(Float)
    split_656_e = Column(Float)

    split_654_a = Column(Float)
    split_655_a = Column(Float)
    split_656_a = Column(Float)

    split_654_p = Column(Float)
    split_655_p = Column(Float)
    split_656_p = Column(Float)
    split_method_used = Column(String(length=50))
    split_sum = Column(Float)  # sum of all split sums, controll for errors
    split_sum_error = Column(Float)  # sum of all split sums, controll for errors   sum - split_sum_e = error in sum


class SplitMethods_dbo(Base):
    __tablename__ = 'split_methods'
    """ db model for split methods.
     Specifikation för hur en viss typ av utrustning ska delas upp i olika kostnads kategorier."""
    id = Column(Integer, primary_key=True)
    tjanst = Column(String(length=50))
    method_to_use = Column(String(length=50))


def create_all_tables(echo: bool = False):
    """ create all tables in db. """
    creds = get_cred(account_file_name="mysql_root_local")
    engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/eunomia", echo=False)
    Base.metadata.create_all(engine)


def drop_all_tables(echo: bool = False):
    """ drop all tables in db. """
    creds = get_cred(account_file_name="mysql_root_local")
    engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/eunomia", echo=False)
    Base.metadata.drop_all(engine)


def reset_mysql_db(echo=False):
    """reset database """
    drop_all_tables(echo=echo)
    create_all_tables(echo=echo)
    print("MySql DB reset done.")


if __name__ == '__main__':
    pass
    # reset_mysql_db()

    # # Test
    from db.mysql_db import init_db

    session = init_db()
    lyam_staff = session.query(Staff_dbo).filter(Staff_dbo.user_id == "lyadol").first()
    print(lyam_staff.get_birth_year())
    print(lyam_staff.get_birth_month())
    print(lyam_staff.get_birth_day())

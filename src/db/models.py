from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, SmallInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base

from utils.creds import get_cred
from utils.pnr_utils import pnr10_to_pnr12

Base = declarative_base()


class Staff_dbo(Base):
    """ db model for staff members. """
    __tablename__ = 'staff'

    id: int = Column(Integer, primary_key=True)
    user_id: str = Column(String(length=10))
    first_name: str = Column(String(length=50))
    last_name: str = Column(String(length=50))
    full_name: str = Column(String(length=70))
    telefon: str = Column(String(length=20))
    u_created_date = Column(DateTime)
    u_changed_date = Column(DateTime)
    titel: str = Column(String(length=30))
    domain: str = Column(String(length=50))
    pnr12: str = Column(String(length=15))
    email: str = Column(String(length=50))
    aktivitet: str = Column(String(length=1))

    @property
    def pnr10(self) -> str:
        """ get pnr10. """
        return self.pnr12[2:]

    def set_pnr12_with_pnr10(self, pnr10: str) -> None:
        """ set pnr12 with pnr10. """
        self.pnr12 = pnr10_to_pnr12(pnr10)

    def __repr__(self):
        return f"Staff(id:{self.id}|user_id='{self.user_id}', first_name='{self.first_name}', last_name='{self.last_name}', pnr12='{self.pnr12}'), , pnr10='{self.pnr10}')"

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
                "pnr": self.pnr12,
                "email": self.email}

    @property
    def birth_year(self) -> int:
        """ get birth year. """
        return int(self.pnr12[0:4])

    @property
    def birth_month(self) -> int:
        """ get numeric birth month. """
        return int(self.pnr12[4:6])

    @property
    def birth_day(self) -> int:
        """ get numeric birth day. """
        return int(self.pnr12[6:8])


class Tjf_dbo(Base):
    """ db model for tjf. """
    __tablename__ = 'tjf'
    id: int = Column(Integer, primary_key=True)
    pnr12: str = Column(String(length=12))
    user_id: str = Column(String(length=6))
    id_komplement_pa: str = Column(String(length=6))
    year: int = Column(SmallInteger)
    month: int = Column(SmallInteger)
    aktivitet_s: str = Column(String(length=1))
    aktivitet: str = Column(String(length=50))
    namn: str = Column(String(length=50))
    yrke: str = Column(String(length=50))

    jan: float = Column(Float)
    feb: float = Column(Float)
    mar: float = Column(Float)
    apr: float = Column(Float)
    maj: float = Column(Float)
    jun: float = Column(Float)
    jul: float = Column(Float)
    aug: float = Column(Float)
    sep: float = Column(Float)
    okt: float = Column(Float)
    dec: float = Column(Float)
    kommentar: str = Column(String(length=150))
    personalkategori: str = Column(String(length=50))


class Student_dbo(Base):
    """ db model for students. """
    __tablename__ = 'student'
    id: int = Column(Integer, primary_key=True)
    user_id: str = Column(String(length=9))
    first_name: str = Column(String(length=50))
    last_name: str = Column(String(length=50))
    pnr: str = Column(String(length=12))
    google_pw: str = Column(String(length=50))
    eduroam_pw: str = Column(String(length=10))
    eduroam_pw_gen_date = Column(DateTime(timezone=True))
    klass: str = Column(String(length=50))

    @property
    def email(self):
        """ get student email """
        return self.user_id + "@edu.linkoping.se"


class FakturaRad_dbo(Base):
    """ db model for faktura rad. """
    __tablename__ = 'faktura_rader'
    id: int = Column(Integer, primary_key=True)
    tjanst: str = Column(String(length=50))
    kundnummer: int = Column(Integer)
    fakturamarkning: str = Column(String(length=50))
    fakturakod: str = Column(String(length=50))
    anvandare: str = Column(String(length=50))
    avser: str = Column(String(length=50))
    period: str = Column(String(length=6))
    antal: int = Column(Integer)
    pris: float = Column(Float)
    Summa: float = Column(Float)  # fakturans summans rad
    split_done: bool = Column(Boolean)  # Has row been split into sub sums?
    split_654_e: float = Column(Float)
    split_655_e: float = Column(Float)
    split_656_e: float = Column(Float)

    split_654_a: float = Column(Float)
    split_655_a: float = Column(Float)
    split_656_a: float = Column(Float)

    split_654_p: float = Column(Float)
    split_655_p: float = Column(Float)
    split_656_p: float = Column(Float)
    split_method_used: str = Column(String(length=50))
    split_sum: float = Column(Float)  # sum of all split sums, controll for errors
    split_sum_error: float = Column(
        Float)  # sum of all split sums, controll for errors   sum - split_sum_e = error in sum


class SplitMethods_dbo(Base):
    """ db model for split methods. """
    __tablename__ = 'split_methods'
    """ db model for split methods.
     Specifikation för hur en viss typ av utrustning ska delas upp i olika kostnads kategorier."""
    id: int = Column(Integer, primary_key=True)
    tjanst: str = Column(String(length=50))
    method_to_use: str = Column(String(length=50))


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
    reset_mysql_db()

    # # Test
    # from db.mysql_db import init_db

    # session = init_db()
    # Staff_dbo.create(session, user_id="test", first_name="test", last_name="test", pnr="test", email="test")
    # lyam_staff = session.query(Staff_dbo).filter(Staff_dbo.user_id == "lyadol").first()
    # print(lyam_staff.get_birth_year())
    # print(lyam_staff.get_birth_month())
    # print(lyam_staff.get_birth_day())

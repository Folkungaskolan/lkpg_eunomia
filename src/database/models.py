"""
MySQL database models
"""
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, SmallInteger
from sqlalchemy.ext.declarative import declarative_base

from database.mysql_db import create_db_engine, MysqlDb

Base = declarative_base()


class Student_id_process_que_dbo(Base):
    """ student id proccess que """
    __tablename__ = 'student_id_process_que_dbo'
    id = Column(Integer, primary_key=True)
    web_id = Column(String(255), nullable=False)
    taken = Column(Boolean, nullable=False, default=False)


class Student_dbo(Base):
    """ database model for student """
    __tablename__ = 'student'
    user_id: str = Column(String(length=10), primary_key=True)
    google_pw: str = Column(String(length=45))
    eduroam_pw: str = Column(String(length=10))
    first_name: str = Column(String(length=50))
    last_name: str = Column(String(length=50))
    eduroam_pw_gen_date = Column(DateTime)
    birthday = Column(DateTime)
    klass: str = Column(String(length=45))
    skola: str = Column(String(length=45))
    last_web_import = Column(DateTime)
    webid: str = Column(String(length=45))
    klass_examen_year: int = Column(Integer, default=0)

    @property
    def email(self) -> str:
        """ Returns the email address for the student """
        return f"{self.user_id}@edu.linkoping.se"


class Student_old_dbo(Base):
    """ database model for student """
    __tablename__ = 'student_old'
    user_id: str = Column(String(length=10), primary_key=True)
    google_pw: str = Column(String(length=45))
    eduroam_pw: str = Column(String(length=10))
    first_name: str = Column(String(length=50))
    last_name: str = Column(String(length=50))
    eduroam_pw_gen_date = Column(DateTime)
    birthday = Column(DateTime)
    klass: str = Column(String(length=45))
    skola: str = Column(String(length=45))
    last_web_import = Column(DateTime)
    webid: str = Column(String(length=45))
    old = Column(DateTime)  # om denna är satt så är eleven gammal och hittas inte längre på webbsidan Detta är när den flyttades datum
    klass_examen_year: int = Column(Integer, default=0)

    @property
    def email(self) -> str:
        """ Returns the email address for the student """
        return f"{self.user_id}@edu.linkoping.se"


class Staff_dbo(Base):
    """ database model for staff members. """
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
    aktivitet_char: str = Column(String(length=1))

    @property
    def pnr10(self) -> str:
        """ get pnr10. """
        return self.pnr12[2:]

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
    """ database model for tjf. """
    __tablename__ = 'tjf'
    id: int = Column(Integer, primary_key=True)
    pnr12: str = Column(String(length=12))
    id_komplement_pa: str = Column(String(length=6))
    year: int = Column(SmallInteger)
    aktivitet: str = Column(String(length=10))
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

    def __repr__(self):
        return F"Tjf(id:{self.id}|pnr12='{self.pnr12}', user_id='{self.user_id}', id_komplement_pa='{self.id_komplement_pa}', year={self.year}, month={self.month}, aktivitet_s='{self.aktivitet_s}', aktivitet='{self.aktivitet}', namn='{self.namn}', yrke='{self.yrke}', jan={self.jan}, feb={self.feb}, mar={self.mar}, apr={self.apr}, maj={self.maj}, jun={self.jun}, jul={self.jul}, aug={self.aug}, sep={self.sep}, okt={self.okt}, dec={self.dec}, kommentar='{self.kommentar}', personalkategori='{self.personalkategori}')"


class FakturaRad_dbo(Base):
    """ database model for faktura rad. """
    __tablename__ = 'faktura_rader'
    id: int = Column(Integer, primary_key=True)
    faktura_year: int = Column(SmallInteger)
    faktura_month: int = Column(SmallInteger)
    tjanst: str = Column(String(length=150))
    avser: str = Column(String(length=150))
    anvandare: str = Column(String(length=150))
    kundnummer: int = Column(Integer)
    fakturamarkning: str = Column(String(length=50))
    fakturakod: str = Column(String(length=50))
    antal: int = Column(Integer)
    pris: float = Column(Float)
    summa: float = Column(Float)  # fakturans summans rad
    split_done: int = Column(Integer, default=False)  # Has row been split into sub sums?
    split_method_used: str = Column(String(length=50))

    # sum of all split sums, control for errors
    split_sum: float = Column(Float)

    # sum of all split sums, control for errors   sum - split_sum_e = error in sum
    split_sum_error: float = Column(Float)

    def __str__(self):
        return F"FakturaRad_dbo(tjanst={self.tjanst},kundnummer={self.kundnummer},fakturamarkning={self.fakturamarkning},fakturakod={self.fakturakod},anvandare={self.anvandare},avser={self.avser},faktura_year={self.faktura_year},faktura_month={self.faktura_month},antal={self.antal},pris={self.pris},summa={self.summa},split_done={self.split_done},split_654_e={self.split_654_e},split_655_e={self.split_655_e},split_656_e={self.split_656_e},split_654_a={self.split_654_a},split_655_a={self.split_655_a},split_656_a={self.split_656_a},split_654_p={self.split_654_p},split_655_p={self.split_655_p},split_656_p={self.split_656_p},split_method_used={self.split_method_used},split_sum={self.split_sum},split_sum_error={self.split_sum_error})"

    def __repr__(self):
        return F"FakturaRad_dbo(tjanst={self.tjanst},kundnummer={self.kundnummer},fakturamarkning={self.fakturamarkning},fakturakod={self.fakturakod},anvandare={self.anvandare},avser={self.avser},faktura_year={self.faktura_year},faktura_month={self.faktura_month},antal={self.antal},pris={self.pris},summa={self.summa},split_done={self.split_done},split_654_e={self.split_654_e},split_655_e={self.split_655_e},split_656_e={self.split_656_e},split_654_a={self.split_654_a},split_655_a={self.split_655_a},split_656_a={self.split_656_a},split_654_p={self.split_654_p},split_655_p={self.split_655_p},split_656_p={self.split_656_p},split_method_used={self.split_method_used},split_sum={self.split_sum},split_sum_error={self.split_sum_error})"


class FakturaRadSplit_dbo(Base):
    """ Sparar delningen av en faktura rad."""
    __tablename__ = 'faktura_rader_split'
    id: int = Column(Integer, primary_key=True)
    split_id: int = Column(Integer)  # id of faktura rad
    faktura_year: int = Column(SmallInteger)
    faktura_month: int = Column(SmallInteger)
    tjanst: str = Column(String(length=150))  # katregori
    avser: str = Column(String(length=150))  # vilken utrustning eller tjänst som faktureras
    anvandare: str = Column(String(length=150))  # i de fall användaren är känd
    split_summa: float = Column(Float)  # fakturans summans rad
    id_komplement_pa: str = Column(String(length=50))  # "655119", osv
    aktivitet: str = Column(String(length=50))  # "p": "410200" osv


class StudentCount_dbo(Base):
    """ Spara antal studenter per månad """
    __tablename__ = 'student_count'
    id: int = Column(Integer, primary_key=True)
    year: int = Column(SmallInteger)
    month: int = Column(SmallInteger)
    id_komplement_pa: str = Column(String(length=10))
    count: int = Column(Integer)


class RunTime_dbo(Base):
    """ Spara runtime data för funktionerna """
    __tablename__ = 'function_run_times'
    id: int = Column(Integer, primary_key=True)
    run_date: datetime = Column(DateTime)
    function_name: str = Column(String(length=50))
    list_length: int = Column(Integer)
    run_time_sec: float = Column(Float)
    avg_time_sec: float = Column(Float)


class FasitCopy(Base):
    """ Spara fasit kopia"""
    __tablename__ = "fasit_copy"

    name: str = Column(String(length=150), primary_key=True)
    color: str = Column(String(length=150))
    unmanaged: str = Column(String(length=150))
    status: str = Column(String(length=150))
    attribute_adress: str = Column(String(length=150))
    attribute_anvandare: str = Column(String(length=150))
    attribute_anvandarnamn: str = Column(String(length=150))
    attribute_byggnad: str = Column(String(length=150))
    attribute_delad: str = Column(String(length=150))
    attribute_domain: str = Column(String(length=150))
    attribute_elev: str = Column(String(length=150))
    attribute_elev_epost: str = Column(String(length=150))
    attribute_epost: str = Column(String(length=150))
    attribute_faktura: str = Column(String(length=150))
    attribute_fakturakod: str = Column(String(length=150))
    attribute_faktureras_ej: str = Column(String(length=150))
    attribute_fasit_admin: str = Column(String(length=150))
    attribute_fasit_admin_html: str = Column(String(length=150))
    attribute_hyresperiodens_slut: str = Column(String(length=150))
    attribute_it_kontakt: str = Column(String(length=150))
    attribute_jobbtitel: str = Column(String(length=150))
    attribute_klass: str = Column(String(length=150))
    attribute_kund: str = Column(String(length=150))
    attribute_kundnummer: str = Column(String(length=150))
    attribute_mobilnummer: str = Column(String(length=150))
    attribute_modell: str = Column(String(length=150))
    attribute_mottagare_av_faktura: str = Column(String(length=150))
    attribute_mottagare_av_fakturaspecifikation: str = Column(String(length=150))
    attribute_noteringar: str = Column(String(length=250))
    attribute_plats: str = Column(String(length=150))
    attribute_senast_inloggade: str = Column(String(length=150))
    attribute_senast_online: str = Column(String(length=150))
    attribute_serienummer: str = Column(String(length=150))
    attribute_servicestatus: str = Column(String(length=150))
    attribute_servicestatus_full: str = Column(String(length=150))
    attribute_skola: str = Column(String(length=150))
    attribute_tillverkare: str = Column(String(length=150))
    attribute_tjanster: str = Column(String(length=150))
    attribute_aterlamnings_datum: str = Column(String(length=150))
    tag_anknytning: int = Column(Integer, default=False)
    tag_anvandare: int = Column(Integer, default=False)
    tag_chromebook: int = Column(Integer, default=False)
    tag_chromebox: int = Column(Integer, default=False)
    tag_dator: int = Column(Integer, default=False)
    tag_domain: int = Column(Integer, default=False)
    tag_faktura: int = Column(Integer, default=False)
    tag_funktionskonto: int = Column(Integer, default=False)
    tag_kund: int = Column(Integer, default=False)
    tag_mobiltelefon: int = Column(Integer, default=False)
    tag_pekplatta: int = Column(Integer, default=False)
    tag_person: int = Column(Integer, default=False)
    tag_plats: int = Column(Integer, default=False)
    tag_rcard: int = Column(Integer, default=False)
    tag_skrivare: int = Column(Integer, default=False)
    tag_skarm: int = Column(Integer, default=False)
    tag_tv: int = Column(Integer, default=False)
    tag_utrustning: int = Column(Integer, default=False)
    tag_videoprojektor: int = Column(Integer, default=False)
    eunomia_update_web: int = Column(Integer, default=False)  # if eunomia changed a value spread updates to web
    eunomia_user_id: str = Column(String(length=20))  # eunomia version of user id
    eunomia_update_web_command: int = Column(String(length=200))
    # Ska innehålla sträng med vilka variabler som ska uppdateras på webben
    # data från databasen till webben

def create_all_tables(echo: bool = False):
    """ create all tables in database. """
    engine = create_db_engine(echo=echo)
    Base.metadata.create_all(engine)


def drop_all_tables(echo: bool = False):
    """ drop all tables in database. """
    engine = create_db_engine(echo=echo)
    Base.metadata.drop_all(engine)


def reset_mysql_db(echo=False):
    """reset database """
    drop_all_tables(echo=echo)
    create_all_tables(echo=echo)
    print("MySql DB reset done.")


def demo_distinct(echo: bool = False) -> None:
    """ demo av join """
    session = MysqlDb().session()
    results = session.query(FakturaRad_dbo.tjanst).distinct().all()
    for result in results:
        print(result.tjanst)


def demo_join() -> None:
    """ demo av join https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.join"""
    session = MysqlDb().session()
    results = session.query(Tjf_dbo, Staff_dbo.aktivitet_char).join(Staff_dbo, Tjf_dbo.pnr12 == Staff_dbo.pnr12) \
        .limit(5).all()
    for result in results:
        print(f"Tjf_dbo{result.Tjf_dbo} Staff_dbo{result.aktivitet_char}")


if __name__ == '__main__':
    pass
    # print(demo_distinct(echo=True))
    create_all_tables(echo=True)
    # reset_mysql_db(echo=True)

    # # Test
    # from database.mysql_db import init_db

    # session = init_db()
    # Staff_dbo.create(session, user_id="test", first_name="test", last_name="test", pnr="test", email="test")
    # lyam_staff = session.query(Staff_dbo).filter(Staff_dbo.user_id == "lyadol").first()
    # print(lyam_staff.get_birth_year())
    # print(lyam_staff.get_birth_month())
    # print(lyam_staff.get_birth_day())

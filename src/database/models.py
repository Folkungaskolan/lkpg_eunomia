"""
MySQL database models
"""
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, SmallInteger, func
from sqlalchemy.ext.declarative import declarative_base

from database.mysql_db import create_db_engine, MysqlDb
from utils.EunomiaEnums import EnhetsAggregering, Aktivitet, FakturaRadState, Skola

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

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return F"user_id: {self.user_id}, first_name: {self.first_name}, last_name: {self.last_name}, klass: {self.klass}, skola: {self.skola}, birthday: {self.birthday}, eduroam_pw: {self.eduroam_pw}, pw: {self.google_pw}, klass_examen_year: {self.klass_examen_year}"

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


class TjanstKategori_dbo(Base):
    """ database model for tjanst kategori """
    __tablename__ = 'tjanst_kategori'
    id = Column(Integer, primary_key=True)
    tjanst: str = Column(String(length=45))
    tjanst_kategori_lvl1: str = Column(String(length=45), default="ej kategoriserad")
    tjanst_kategori_lvl2: str = Column(String(length=45), default="ej kategoriserad")
    beskrivning: str = Column(String(length=255))


class Staff_dbo(Base):
    """ database model for staff members. """
    __tablename__ = 'staff'

    id: int = Column(Integer, primary_key=True)
    user_id: str = Column(String(length=10))
    first_name: str = Column(String(length=50))
    last_name: str = Column(String(length=50))
    full_name: str = Column(String(length=70))  # FASIT Namnet .attribute_anvandare
    telefon: str = Column(String(length=20))
    u_created_date = Column(DateTime)
    u_changed_date = Column(DateTime)
    titel: str = Column(String(length=30))
    domain: str = Column(String(length=50))
    pnr12: str = Column(String(length=15))
    email: str = Column(String(length=50))
    aktivitet_char: str = Column(String(length=1))
    sum_tjf_jan: float = Column(Float, default=0)  # Vilka månader som ser konstiga ut
    sum_tjf_feb: float = Column(Float, default=0)
    sum_tjf_mar: float = Column(Float, default=0)
    sum_tjf_apr: float = Column(Float, default=0)
    sum_tjf_maj: float = Column(Float, default=0)
    sum_tjf_jun: float = Column(Float, default=0)
    sum_tjf_jul: float = Column(Float, default=0)
    sum_tjf_aug: float = Column(Float, default=0)
    sum_tjf_sep: float = Column(Float, default=0)
    sum_tjf_okt: float = Column(Float, default=0)
    sum_tjf_nov: float = Column(Float, default=0)
    sum_tjf_dec: float = Column(Float, default=0)
    tjf_error: str = Column(String(length=45), default="0")
    skola: str = Column(String(length=45))

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
        """ get numeric birthday. """
        return int(self.pnr12[6:8])


class StaffSubjects_dbo(Base):
    """ Vilka ämnen har varje lärare """
    __tablename__ = 'staff_subjects'
    id: int = Column(Integer, primary_key=True)
    subject: str = Column(String(length=10))
    kategori: str = Column(String(length=20))
    klass_grupp: str = Column(String(length=20))
    user_id: str = Column(String(length=50))
    first_name: str = Column(String(length=50))
    last_name: str = Column(String(length=50))
    email: str = Column(String(length=50))


class StaffMentors_dbo(Base):
    """ Vilka ämnen har varje lärare """
    __tablename__ = 'staff_mentors'
    id: int = Column(Integer, primary_key=True)
    user_id: str = Column(String(length=50))
    class_name: str = Column(String(length=50))
    class_level: str = Column(String(length=50))
    class_in_gru: int = Column(Integer, default=0)
    class_in_gy: int = Column(Integer, default=0)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    latest_import_made = Column(String(length=50), onupdate=func.now())


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
    nov: float = Column(Float)
    dec: float = Column(Float)
    kommentar: str = Column(String(length=150))
    personalkategori: str = Column(String(length=50))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return F"Tjf(id:{self.id}|pnr12='{self.pnr12}', id_komplement_pa='{self.id_komplement_pa}', year={self.year},  jan={self.jan}, feb={self.feb}, mar={self.mar}, apr={self.apr}, maj={self.maj}, jun={self.jun}, jul={self.jul}, aug={self.aug}, sep={self.sep}, okt={self.okt}, dec={self.dec}, kommentar='{self.kommentar}', personalkategori='{self.personalkategori}')"


class FakturaRad_dbo(Base):
    """ database model for faktura rad. """
    __tablename__ = 'faktura_rader'
    id: int = Column(Integer, primary_key=True)
    faktura_year: int = Column(SmallInteger)
    faktura_month: int = Column(SmallInteger)
    tjanst: str = Column(String(length=150))  # kategori för grej
    avser: str = Column(String(length=150))  # specifik för grej
    anvandare: str = Column(String(length=150))  # om fasit har användare
    kundnummer: int = Column(Integer)
    fakturamarkning: str = Column(String(length=50))
    fakturakod: str = Column(String(length=50))
    antal: int = Column(Integer)  # hur många av något i summeringar
    pris: float = Column(Float)  # pris per enhet
    summa: float = Column(Float)  # fakturans summans rad
    split_done: int = Column(Integer, default=False)  # Has row been split into sub sums?
    split_method_used: str = Column(String(length=150))

    # sum of all split sums, control for errors
    split_sum: float = Column(Float)

    # sum of all split sums, control for errors   sum - split_sum_e = error in sum
    split_sum_error: float = Column(Float)

    eunomia_row: int = Column(Integer)  # row in eunomia file
    eunomia_case_id: str = Column(String(length=50))  # konto in eunomia file
    eunomia_case_creator_user_id: str = Column(String(length=50))  # konto in eunomia file
    tjanst_kategori_lvl1: str = Column(String(length=150))  # kategori grej
    tjanst_kategori_lvl2: str = Column(String(length=150))  # kategori grej

    dela_over_enheter: list[str | EnhetsAggregering] = None  # spara vilka enheter som
    split_status: FakturaRadState = FakturaRadState.SPLIT_INCOMPLETE
    skola: Skola = Skola.UNKNOWN  # skola som raden tillhör
    user_id: str = None
    user_aktivitet_char: Aktivitet = Aktivitet.N
    split: dict[str, float] = {}
    split_conditions: list[str] = ["self.faktura_year is not None", # AUTO set from start
                                   "self.faktura_year > 2021",# AUTO set from start
                                   "self.faktura_year < 2025",# AUTO set from start
                                   "self.faktura_month is not None",# AUTO set from start
                                   "self.faktura_month > 0",# AUTO set from start
                                   "self.faktura_month < 13",# AUTO set from start
                                   "self.tjanst is not None",# AUTO set from start
                                   "len(self.tjanst) > 0",# AUTO set from start
                                   "self.avser is not None",# AUTO set from start
                                   "len(self.avser) > 0",# AUTO set from start
                                   "self.anvandare is not None",# AUTO set from start
                                   "len(self.anvandare) > 0",# AUTO set from start
                                   "self.pris",# AUTO set from start
                                   "self.pris > 0",# AUTO set from start
                                   "self.summa is not None",# AUTO set from start
                                   "self.summa > 0",# AUTO set from start

                                   "self.split_status != FakturaRadState.SPLIT_INCOMPLETE", # Status bärare
                                   "self.split_method_used is not None", "len(self.split_method_used) > 1", # Måste sättas
                                   "self.split is not None","len(self.split) > 0", # Måste sättas
                                   "Aktivitet(self.user_aktivitet_char) in {Aktivitet.P, Aktivitet.A, Aktivitet.E}" # Behöver en godkänd aktivitet
                                   ]

    def ready_to_be_split(self, verbose:bool = False) -> bool:
        """ is row ready to be split? """
        for c in self.split_conditions:
            if eval(c) is False:
                # print()
                # print(F"{c} : {eval(c)}")
                return False
        return True

    def print_delnings_status(self):
        """ print status of split. """
        for c in self.split_conditions:
            print(F"{c} : {eval(c)}")
    def print_split_status(self):
        """ print status of split. """
        print(F"self.split_status: {self.split_status=}")
    def success(self):
        """ Sammantaget, är delningen lyckad? """
        s = {self.split_status == FakturaRadState.SPLIT_BY_FASIT_USER_SUCCESSFUL,
             self.split_status == FakturaRadState.SPLIT_BY_FASIT_KONTERING_SUCCESSFUL,
             self.split_status == FakturaRadState.SPLIT_BY_GENERELL_TFJ_SUCCESSFUL,
             self.split_status == FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL}
        return any(s)

    def __str__(self):
        return F"FakturaRad_dbo({self.id=} {self.tjanst:},kundnummer={self.kundnummer},fakturamarkning={self.fakturamarkning},fakturakod={self.fakturakod}," \
               F"anvandare={self.anvandare},avser={self.avser},faktura_year={self.faktura_year},faktura_month={self.faktura_month},antal={self.antal},pris={self.pris},summa={self.summa},split_done={self.split_done}tag_,split_method_used={self.split_method_used},split_sum={self.split_sum},split_sum_error={self.split_sum_error})"

    def __repr__(self):
        return F"FakturaRad_dbo({self.id=} {self.tjanst:},kundnummer={self.kundnummer},fakturamarkning={self.fakturamarkning},fakturakod={self.fakturakod}," \
               F"anvandare={self.anvandare},avser={self.avser},faktura_year={self.faktura_year},faktura_month={self.faktura_month},antal={self.antal},pris={self.pris},summa={self.summa},split_done={self.split_done}tag_,split_method_used={self.split_method_used},split_sum={self.split_sum},split_sum_error={self.split_sum_error})"


class FakturaRadSplit_dbo(Base):
    """ Sparar delningen av en faktura rad."""
    __tablename__ = 'faktura_rader_split'
    id: int = Column(Integer, primary_key=True)
    split_id: int = Column(Integer)  # id of faktura rad som delats
    faktura_year: int = Column(SmallInteger)
    faktura_month: int = Column(SmallInteger)
    tjanst: str = Column(String(length=150))  # kategori
    avser: str = Column(String(length=150))  # vilken utrustning eller tjänst som faktureras
    anvandare: str = Column(String(length=150))  # i de fall användaren är känd
    split_summa: float = Column(Float)  # fakturans summans rad för denna enhet och aktivitet
    id_komplement_pa: str = Column(String(length=50))  # "655119", osv
    split_method_used: str = Column(String(length=150))
    aktivitet: str = Column(String(length=50))  # "p": "410200" osv
    tjanst_kategori_lvl1: str = Column(String(length=45), default="ej kategoriserad")
    tjanst_kategori_lvl2: str = Column(String(length=45), default="ej kategoriserad")


class StudentCount_dbo(Base):
    """ Spara antal studenter per månad """
    __tablename__ = 'student_count'
    id: int = Column(Integer, primary_key=True)
    year: int = Column(SmallInteger)
    month: int = Column(SmallInteger)
    id_komplement_pa: str = Column(String(length=10))
    count: int = Column(Integer)


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

    eunomia_user_id: str = Column(String(length=20))  # eunomia version of user id
    eunomia_update_web_command: int = Column(String(length=200))
    # Ska innehålla sträng med vilka variabler som ska uppdateras på webben
    # data från databasen till webben
    eunomia_kontering: str = Column(String(length=100))
    eunomia_gear_missing_in_fasit: str = Column(String(length=100))  # om det saknas utrustning i fasit

    def dela_pa_gen_tjf(self):
        """ Dela upp på generell tjänstefördelning"""
        b = {self.tag_anknytning == 1,
             self.tag_rcard == 1,
             self.tag_mobiltelefon == 1,
             self.tag_skrivare == 1}
        return any(b)

    def dela_pa_elevantal(self):
        """
        Ska raden delas på generellt elevantal eller ej
        :return: Bool
        :rtype:
        """
        b = {self.tag_chromebox == 1,
             self.tag_domain == 1,
             self.tag_videoprojektor == 1,
             self.tag_funktionskonto == 1}
        return any(b)

    def __str__(self):
        return self.__repr__

    def __repr__(self):
        """ Repr för fasit rad"""
        return f"{self.name}, {self.status}, {self.attribute_anvandare}, {self.attribute_anvandarnamn},  {self.attribute_epost},  {self.attribute_hyresperiod}"

    def create_all_tables(echo: bool = False):
        """ create all tables in database. """
        engine = create_db_engine(echo=echo)
        Base.metadata.create_all(engine)

    class RunTime_dbo(Base):
        """ Spara runtime data för funktionerna """
        __tablename__ = 'function_run_times'
        id: int = Column(Integer, primary_key=True)
        run_date: datetime = Column(DateTime)
        function_name: str = Column(String(length=50))
        list_length: int = Column(Integer)
        run_time_sec: float = Column(Float)
        avg_time_sec: float = Column(Float)

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

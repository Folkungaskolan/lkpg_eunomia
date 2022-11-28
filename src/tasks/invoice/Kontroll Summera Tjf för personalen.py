""" Summera tjf för personalen kontrollera att ingen jobbar mer än 100 %"""
import MySQLdb
from sqlalchemy import and_

from database.models import Tjf_dbo, Staff_dbo
from database.mysql_db import MysqlDb

MONTHS_name_to_int = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "maj": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}
MONTHS_int_to_name = {v: k for k, v in MONTHS_name_to_int.items()}


def calc_tjf_sums() -> None:
    """ Summera tjf för personalen """
    s = MysqlDb().session()
    staff_pnrs = s.query(Tjf_dbo.pnr12).distinct().all()  # hämta alla personnummer
    # staff_pnrs = s.query(Tjf_dbo.pnr12).filter(Tjf_dbo.pnr12 == "123456789123").distinct().all() # för testning
    for pnr in staff_pnrs:
        # print(pnr.pnr12)
        tjfs = s.query(Tjf_dbo).filter(Tjf_dbo.pnr12 == pnr.pnr12).all()
        tjfa_sum = {k: 0.0 for k in MONTHS_name_to_int.keys()}

        for tjf in tjfs:
            for month_name in MONTHS_name_to_int.keys():  # jan,feb,mar,apr,maj,jun,jul,aug,sep,okt,nov,dec
                if eval(F"tjf.{month_name}") is None:  # jan,feb,mar,apr,maj,jun,jul,aug,sep,okt,nov,dec
                    tjfa_sum[month_name] += extrapolera_tjf(pnr12=pnr.pnr12,
                                                            id_komplement_pa=tjf.id_komplement_pa,
                                                            month_nr=MONTHS_name_to_int[month_name])
                    exec(F'tjf.{month_name} = tjfa_sum["{month_name}"]')  # kör tjf.jan = tjfa_sum[{"jan"}]
                else:
                    tjfa_sum[month_name] += eval(F"tjf.{month_name}")

        staffer = s.query(Staff_dbo).filter(Staff_dbo.pnr12 == pnr.pnr12).first()
        if staffer is None:
            staffer = Staff_dbo(pnr12=pnr.pnr12)
            staffer.domain = "tjf_import"
        for month_name in MONTHS_name_to_int.keys():  # jan,feb,mar,apr,maj,jun,jul,aug,sep,okt,nov,dec
            exec(F'staffer.sum_tjf_{month_name} = tjfa_sum["{month_name}"]')  # kör staffer.sum_tjf_jan = tjfa_sum[{"jan"}]
        s.add(staffer)
    s.commit()
    mark_tjf_errors()


def extrapolera_tjf(pnr12: str, id_komplement_pa: str, month_nr: int, riktning: str = "ner") -> float:
    """ Extrapolera tjf för personalen
     försöker först hitta tjf "tidigre" i tiden, om det inte finns så försöker den hitta "senare" i tiden
     """
    # print(f"{pnr12:}, {id_komplement_pa}, {month_nr:}")
    s = MysqlDb().session()
    if month_nr < 1:  # om vi gått hela vägen upp, och inte hittat ett värde att extrapolera med byt riktning
        return extrapolera_tjf(pnr12=pnr12, id_komplement_pa=id_komplement_pa, month_nr=1, riktning="upp")
    if month_nr > 12:  # Inget hittat: returnera 0
        return 0.0
    tjf = s.query(Tjf_dbo).filter(and_(Tjf_dbo.pnr12 == pnr12, Tjf_dbo.id_komplement_pa == id_komplement_pa)).first()
    # print(tjf)
    # print(F'month nr: {month_nr}:{eval(F"tjf.{MONTHS_int_to_name[month_nr]}")}')

    if eval(F"tjf.{MONTHS_int_to_name[month_nr]}") is None:
        if riktning == "upp":
            new_month = riktning = month_nr + 1
        else:
            new_month = riktning = month_nr - 1
        return extrapolera_tjf(pnr12=pnr12, id_komplement_pa=id_komplement_pa, month_nr=new_month)
    else:
        return eval(F"tjf.{MONTHS_int_to_name[month_nr]}")


def mark_tjf_errors():
    """ Markera tjf fel om någon tjf är över 100 % """
    s = MysqlDb().session()
    staffers = s.query(Staff_dbo).all()  # hämta alla personnummer
    for staffer in staffers:
        for month_name in MONTHS_name_to_int.keys():
            if eval(F"staffer.sum_tjf_{month_name}") > 1.01:
                staffer.tjf_error = True
            else:
                staffer.tjf_error = False
    s.commit()


if __name__ == '__main__':
    # print(extrapolera_tjf(pnr12="123456789123", id_komplement_pa="321", month_nr=1))
    # print(extrapolera_tjf(pnr12="123456789123", id_komplement_pa="321", month_nr=3))
    # print(extrapolera_tjf(pnr12="123456789123", id_komplement_pa="321", month_nr=9))
    calc_tjf_sums()
    mark_tjf_errors()

""" """
from functools import cache

from sqlalchemy import func, or_

from database.models import TjanstKategori_dbo, FakturaRad_dbo, FakturaRadSplit_dbo
from database.mysql_db import MysqlDb


@cache
def get_kategorier_for(tjanst: str) -> (str, str):
    """    Hämtar alla kategorier    """
    s = MysqlDb().session()
    kategorier = s.query(TjanstKategori_dbo).filter(TjanstKategori_dbo.tjanst == tjanst).first()
    return kategorier.tjanst_kategori_lvl1, kategorier.tjanst_kategori_lvl2


def list_tjanst_with_no_info():
    """ Vilka tjänster saknar info? """
    s = MysqlDb().session()
    tjanster = s.query(TjanstKategori_dbo).filter(or_(TjanstKategori_dbo.tjanst_kategori_lvl1 == None,
                                                      TjanstKategori_dbo.tjanst_kategori_lvl2 == None,
                                                      func.length(TjanstKategori_dbo.tjanst_kategori_lvl1) < 2,
                                                      func.length(TjanstKategori_dbo.tjanst_kategori_lvl1) < 2)
                                                  ).all()

    if len(tjanster) != 0:
        print("Tjänster med korta kategorier")
        for t in tjanster:
            print(F"{t.tjanst=}, {t.tjanst_kategori_lvl1=}, {t.tjanst_kategori_lvl2=}")
    else:
        print("Inga tjänster med korta kategorier eller saknade kategorier hittades ")


def update_kategorier_in_split_table() -> None:
    """ Uppdatera kategorier i split tabellen """
    s = MysqlDb().session()
    tjanster = s.query(TjanstKategori_dbo).all()
    for t in tjanster:
        split_rader = s.query(FakturaRadSplit_dbo).filter(FakturaRadSplit_dbo.tjanst == t.tjanst).all()
        for r in split_rader:
            r.tjanst_kategori_lvl1 = t.tjanst_kategori_lvl1
            r.tjanst_kategori_lvl2 = t.tjanst_kategori_lvl2
    s.commit()


def update_kategorier_in_faktura_table() -> None:
    """ Uppdatera kategorier i faktura tabellen """
    s = MysqlDb().session()
    tjanster = s.query(TjanstKategori_dbo).all()
    for t in tjanster:
        split_rader = s.query(FakturaRad_dbo).filter(FakturaRad_dbo.tjanst == t.tjanst).all()
        for r in split_rader:
            r.tjanst_kategori_lvl1 = t.tjanst_kategori_lvl1
            r.tjanst_kategori_lvl2 = t.tjanst_kategori_lvl2
    s.commit()


def update_kategorier_for_all_tables() -> None:
    """ Uppdatera kategorier i alla tabeller """
    update_kategorier_in_split_table()
    update_kategorier_in_faktura_table()


def copy_distinct_tjansts_to_tjanst_kategorisering():
    """ För gruppering i Pivot """
    s = MysqlDb().session()
    distinct_tjanster = s.query(FakturaRad_dbo.tjanst).distinct().all()
    for en_distinct_tjanst_obj in distinct_tjanster:
        if en_distinct_tjanst_obj.tjanst.startswith("Ärende"):
            continue
        else:
            print(en_distinct_tjanst_obj.tjanst)
            tjanst_rad = s.query(TjanstKategori_dbo).filter(TjanstKategori_dbo.tjanst == en_distinct_tjanst_obj.tjanst).first()
            if tjanst_rad is None:
                s.add(TjanstKategori_dbo(tjanst=en_distinct_tjanst_obj.tjanst))
            else:
                continue
    s.commit()


if __name__ == '__main__':
    print(get_kategorier_for("Kontakt Linköping svarstjänst"))
    print(get_kategorier_for("Pgm Adobe CC for EDU K12"))

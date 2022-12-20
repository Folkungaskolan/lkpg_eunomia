""" Delning av CB fakturor """
import inspect

from sqlalchemy import func, and_, or_

from database.models import FakturaRadSplit_dbo, FakturaRad_dbo
from database.mysql_db import MysqlDb
from settings.enhetsinfo import ID_AKTIVITET
from utils.EunomiaEnums import EnhetsAggregering
from utils.dbutil.student_db import calc_split_on_student_count


def create_split_row_for_cb(year: int, month: int, total_to_split: float, split: list[str:float]) -> None:
    """ Mata in Chromebook fördelningen för givet år och månad """
    s = MysqlDb().session()
    for enhet_id, enhets_share_of_total in split.items():
        s.add(FakturaRadSplit_dbo(
            faktura_year=year,
            faktura_month=month,
            tjanst="Chromebook",
            split_summa=enhets_share_of_total * total_to_split,
            id_komplement_pa=enhet_id,
            aktivitet=ID_AKTIVITET[enhet_id]["p"]
        ))
    s.commit()


def gen_cb_sums() -> None:
    """ Generera summerings rader för Chromebook """
    s = MysqlDb().session()
    sum_cbs = s.query(FakturaRad_dbo.tjanst,
                      FakturaRad_dbo.faktura_year,
                      FakturaRad_dbo.faktura_month,
                      func.sum(FakturaRad_dbo.pris).label("pris_sum"),
                      func.sum(FakturaRad_dbo.antal).label("antal_sum"),
                      func.sum(FakturaRad_dbo.summa).label("summa_sum")
                      ).group_by(FakturaRad_dbo.tjanst,
                                 FakturaRad_dbo.faktura_year,
                                 FakturaRad_dbo.faktura_month
                                 ).filter(and_(FakturaRad_dbo.tjanst.contains("Chromebook"),
                                               FakturaRad_dbo.faktura_month > 6,
                                               ~FakturaRad_dbo.tjanst.startswith("Chromebook summa"),
                                               or_(FakturaRad_dbo.eunomia_row == None,
                                                   FakturaRad_dbo.eunomia_row == 0)
                                               )
                                          ).all()

    for sum_cb in sum_cbs:
        # Skapa en summerings referens
        month_CB_sum = s.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst == "Chromebook summa"),
                                                      FakturaRad_dbo.faktura_year == sum_cb.faktura_year,
                                                      FakturaRad_dbo.faktura_month == sum_cb.faktura_month
                                                      ).first()
        if month_CB_sum is None:
            month_CB_sum = FakturaRad_dbo(
                faktura_year=sum_cb.faktura_year,
                faktura_month=sum_cb.faktura_month,
                tjanst="Chromebook summa",
                pris=float(sum_cb.pris_sum) / float(sum_cb.antal_sum),
                antal=sum_cb.antal_sum,
                summa=sum_cb.summa_sum,
                split_done=True,
                split_method_used="CB")
            s.add(month_CB_sum)
        else:
            month_CB_sum.faktura_year = sum_cb.faktura_year
            month_CB_sum.faktura_month = sum_cb.faktura_month
            month_CB_sum.tjanst = "Chromebook summa"
            month_CB_sum.pris = int(sum_cb.pris_sum / float(sum_cb.antal_sum))
            month_CB_sum.antal = sum_cb.antal_sum
            month_CB_sum.summa = sum_cb.summa_sum
            month_CB_sum.split_done = True
            month_CB_sum.split_method_used = "CB"
        s.commit()


def create_cb_split_rows(verbose: bool = False) -> None:
    """ Skapa split rader för CB """
    s = MysqlDb().session()

    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    sum_rows = s.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst == "Chromebook summa")).all()
    for sum_row in sum_rows:
        split_by_student = calc_split_on_student_count(year=sum_row.faktura_year,
                                                       month=sum_row.faktura_month,
                                                       enheter_to_split_over=EnhetsAggregering.CB
                                                       )
        if round(sum(split_by_student.values()), 3) != 1:  # sum(split_by_student.values()) ska summera till 1 annars har vi fel
            raise ValueError(f"Summan av split_by_student ska vara 1 men är {sum(split_by_student.values())}")
        # Skapa en delning
        for enhet, enhets_andel in split_by_student.items():
            split_row = s.query(FakturaRadSplit_dbo).filter(and_(FakturaRadSplit_dbo.split_id == sum_row.id,
                                                                 FakturaRadSplit_dbo.id_komplement_pa == enhet,
                                                                 FakturaRadSplit_dbo.aktivitet == ID_AKTIVITET[enhet]["p"]
                                                                 )).first()
            if split_row is None:
                s.add(FakturaRadSplit_dbo(faktura_year=sum_row.faktura_year,
                                          faktura_month=sum_row.faktura_month,
                                          split_id=sum_row.id,  # CB kommer ha backreferens till summerings raden TODO
                                          tjanst="Chromebooks",
                                          avser="Chromebooks",
                                          anvandare="Chromebooks",
                                          id_komplement_pa=enhet,
                                          split_summa=enhets_andel * sum_row.pris * sum_row.antal,
                                          aktivitet=ID_AKTIVITET[enhet]["p"]
                                          )
                      )
            else:
                # split_row.year, month, id_komplement_pa, aktivitet # är redan rätt om den hittats
                split_row.split_summa = enhets_andel * sum_row.pris * sum_row.antal
        s.commit()
def mark_cbs_in_invoicing_tbl_as_split():
    """ Markera alla Chromebook raderna som splittade """
    s = MysqlDb().session()
    # sätt alla CB summa rader till split_done
    sum_cbs = s.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst.contains("Chromebook"),
                                                  FakturaRad_dbo.tjanst != "Chromebook summa",
                                                  FakturaRad_dbo.split_done == 0
                                                  )
                                             ).all()
    for sum_cb in sum_cbs:
        sum_cb.split_done = 1

    # sätt alla CB individ rader till split_done
    all_cbs = s.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst.contains("Chromebook"), FakturaRad_dbo.split_done == 0)).all()
    for cb in all_cbs:
        cb.split_done = 1
        cb.split_method_used = "CB"
    s.commit()


def behandla_dela_cb(verbose: bool = False) -> None:
    """ Behandla dela cb för månader med lösa CB rader"""
    gen_cb_sums()  # skapa summerings rader för CB´s
    create_cb_split_rows()
    mark_cbs_in_invoicing_tbl_as_split()


if __name__ == '__main__':
    behandla_dela_cb(verbose=False)

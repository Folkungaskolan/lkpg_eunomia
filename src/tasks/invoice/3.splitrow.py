""" Hanterar uppdelning av fakturarader """
from functools import cache

from sqlalchemy import func, or_
from sqlalchemy.sql.elements import and_

from database.models import FakturaRad_dbo, SplitMethods_dbo, Tjf_dbo, FakturaRadSplit_dbo
from database.mysql_db import MysqlDb
from settings.enhetsinfo import ID_AKTIVITET
from utils.print_progress_bar import print_progress_bar
from utils.student.count_students import count_student, generate_split_on_student_count
from utils.intergration_utils.obsidian import extract_variable_value_from_gear_name


def copy_unique_tjanst():
    """ Kopiera unika tjänster till Split method registret """
    s = MysqlDb().session()

    print(F"start copy_unique_tjanst")
    results = s.query(FakturaRad_dbo.tjanst).distinct().all()
    for result in results:

        exists = s.query(SplitMethods_dbo).filter(SplitMethods_dbo.tjanst == result.tjanst).first()
        if exists is None:
            print(f"adding : {result.tjanst} as new split")
            s.add(SplitMethods_dbo(tjanst=result.tjanst))
            s.commit()
    print(F"end copy_unique_tjanst")
    return s


def split_row() -> None:
    """ split row """
    s = MysqlDb().session()
    behandla_dela_cb()
    rader = s.query(FakturaRad_dbo).filter(FakturaRad_dbo.split_done == None).limit(2).all()
    for rad in rader:
        print(rad)

        print("Dela enligt Fasit ägare")
        print("Dela enligt Fasit Kontering")
        print("Dela enligt Obsidian ägare")
        print("Dela enligt Total Tjf")
        print("Dela enligt Elev antal")


def create_split_row_for_cb(year: int, month: int, total_to_split: float, split: list[str:float]) -> None:
    """ Mata in Chromebook fördelningen för givet år och månad """
    s = MysqlDb().session()
    for key, value in split.items():
        s.add(FakturaRadSplit_dbo(faktura_year=year,
                                  faktura_month=month,
                                  tjanst="Chromebook",
                                  pris=value,
                                  antal=0,
                                  summa=0))
    s.commit()


def behandla_dela_cb() -> None:
    """ Behandla dela cb för månader med lösa CB rader"""
    print("Dela enligt CB")
    s = MysqlDb().session()
    sum_cbs = s.query(FakturaRad_dbo.faktura_year,
                      FakturaRad_dbo.faktura_month,
                      FakturaRad_dbo.tjanst,
                      func.sum(FakturaRad_dbo.pris).label("pris_sum"),
                      func.sum(FakturaRad_dbo.antal).label("antal_sum"),
                      func.sum(FakturaRad_dbo.summa).label("summa_sum")
                      ).group_by(FakturaRad_dbo.tjanst,
                                 FakturaRad_dbo.faktura_year,
                                 FakturaRad_dbo.faktura_month
                                 ).filter(and_(FakturaRad_dbo.tjanst.contains("Chromebook"),
                                               FakturaRad_dbo.faktura_month > 6
                                               )
                                          ).all()
    for sum_cb in sum_cbs:
        # Skapa en summerings referens
        month_CB_sum = s.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst == "Chromebook summa"),
                                                      FakturaRad_dbo.faktura_year == sum_cb.faktura_year,
                                                      FakturaRad_dbo.faktura_month == sum_cb.faktura_month
                                                      ).first()
        if month_CB_sum is None:
            month_CB_sum = FakturaRad_dbo()
            month_CB_sum.faktura_year = sum_cb.faktura_year
            month_CB_sum.faktura_month = sum_cb.faktura_month
            month_CB_sum.tjanst = "Chromebook summa"
            month_CB_sum.pris = sum_cb.pris_sum
            month_CB_sum.antal = sum_cb.antal_sum
            month_CB_sum.summa = sum_cb.summa_sum
            month_CB_sum.split_done = True
            month_CB_sum.split_method_used = "CB"
            s.add(month_CB_sum)
        else:
            month_CB_sum.faktura_year = sum_cb.faktura_year
            month_CB_sum.faktura_month = sum_cb.faktura_month
            month_CB_sum.tjanst = "Chromebook summa"
            month_CB_sum.pris = sum_cb.pris_sum
            month_CB_sum.antal = sum_cb.antal_sum
            month_CB_sum.summa = sum_cb.summa_sum
            month_CB_sum.split_done = True
            month_CB_sum.split_method_used = "CB"
        s.commit()
        # Skapa en split referens
        split_by_student = generate_split_on_student_count(year=sum_cb.year,
                                                           month=sum_cb.faktura_month,
                                                           enheter_to_split_over={"CB"}
                                                           )
        # Skapa en delning
        for enhet, enhets_andel in split_by_student.items():
            s.add(FakturaRadSplit_dbo(faktura_year=sum_cb.faktura_year,
                                      faktura_month=sum_cb.faktura_month,
                                      tjanst="Chromebook",
                                      split_summa=enhets_andel * sum_cb.pris_sum,
                                      aktivitet=ID_AKTIVITET[enhet]["p"],
                                      summa=0)
                  )
            s.commit()
            s = create_split_row_for_cb(year=sum_cb.faktura_year,
                                        month=FakturaRad_dbo.faktura_month,
                                        total_to_split=sum_cb.summa_sum,
                                        split=generate_split_on_student_count(month=sum_cb.faktura_month))

    # sätt alla CB rader till split_done
    sum_cbs = s.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst.contains("Chromebook"),
                                                  FakturaRad_dbo.tjanst != "Chromebook summa",
                                                  FakturaRad_dbo.split_done == 0
                                                  )
                                             ).all()

    for sum_cb in sum_cbs:
        sum_cb.split_done = 1
    s.commit()


def dela_enl_total_tjf(faktura_rad: FakturaRad_dbo) -> None:
    """ Split på total tjf """
    print(f"Dela_enl_total_tjf start")
    s = MysqlDb().session()
    # @cache


def generate_total_tjf_for_month(month: int) -> dict[str:dict[str, float]]:
    """ sum and create a proportion for each tjanstcode in a month """
    s = MysqlDb().session()
    id_komplement_pas_aktivitet_combos = s.query(Tjf_dbo.id_komplement_pa, Tjf_dbo.aktivitet).distinct().all()
    try:
        return process_tjf_totals(combo_list=id_komplement_pas_aktivitet_combos, month=month)
    except ValueError as error:
        for id_komplement_pa, aktivitet in id_komplement_pas_aktivitet_combos:
            if aktivitet is None:
                print(f"id_komplement_pa: {id_komplement_pa}, aktivitet: {aktivitet}")
        raise ValueError from error


def process_tjf_totals(combo_list: list[list[str]], month: int) -> dict[str:dict[str, float]]:
    """ process tjf """
    s = MysqlDb().session()
    abs_total_tjf = {}
    abs_sum_tjf = 0
    MONTHS = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "maj", 6: "jun", 7: "jul", 8: "aug", 9: "sep", 10: "okt", 11: "nov", 12: "dec"}
    for id_komplement_pa, aktivitet in combo_list:
        if aktivitet is None:
            raise ValueError("There are empty numeric aktivitet in tjf")
    tjfs = s.query(Tjf_dbo).filter(and_(Tjf_dbo.id_komplement_pa == id_komplement_pa,
                                        Tjf_dbo.id_komplement_pa == aktivitet)).all()
    combo_tjf_sum = 0
    for tjf in tjfs:
        combo_tjf_sum += getattr(tjf, MONTHS[month])
        abs_sum_tjf += getattr(tjf, MONTHS[month])
    abs_total_tjf[id_komplement_pa] = {aktivitet: combo_tjf_sum}
    rel_tjf = {}
    for id_komplement_pa, aktivitet in combo_list:
        rel_tjf[id_komplement_pa][aktivitet] = abs_total_tjf[id_komplement_pa][aktivitet] / abs_sum_tjf
    return rel_tjf


@cache
def gen_split_numbers_by_elevantal(enheter: set[str] = None, month: int = None, ) -> dict[str:dict[str, float]]:
    """ generate split by elevantal """
    _, rel_split = count_student(endast_id_komplement_pa=enheter, month=month)
    return rel_split


if __name__ == "__main__":
    # gen_split_by_elevantal(enheter=["654300", "654400"])
    # generate_total_tjf_for_month(1)
    behandla_dela_cb()

    # split_row()

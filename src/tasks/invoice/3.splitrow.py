""" Hanterar uppdelning av fakturarader """
from functools import cache

from sqlalchemy import func
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import and_

from database.models import FakturaRad_dbo, SplitMethods_dbo, Tjf_dbo
from database.mysql_db import init_db
from utils.student.count_students import count_student
from utils.intergration_utils.obsidian import extract_variable_value_from_gear_name
from sqlalchemy import update


def copy_unique_tjanst(session: Session = None) -> Session:
    """ Kopiera unika tjänster till Split method registret """
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    print(F"start copy_unique_tjanst")
    results = local_session.query(FakturaRad_dbo.tjanst).distinct().all()
    for result in results:

        exists = local_session.query(SplitMethods_dbo).filter(SplitMethods_dbo.tjanst == result.tjanst).first()
        if exists is None:
            print(f"adding : {result.tjanst} as new split")
            local_session.add(SplitMethods_dbo(tjanst=result.tjanst))
            local_session.commit()
    print(F"end copy_unique_tjanst")
    return local_session


def split_row() -> None:
    """ split row """
    local_session = init_db()
    local_session = behandla_dela_cb(session=local_session)
    rader = local_session.query(FakturaRad_dbo).filter(FakturaRad_dbo.split_done == None).limit(2).all()
    for rad in rader:
        print(rad)

        print("Dela enligt Fasit ägare")
        print("Dela enligt Fasit Kontering")
        print("Dela enligt Obsidian ägare")
        print("Dela enligt Total Tjf")
        print("Dela enligt Elev antal")


def behandla_dela_cb(session: Session = None) -> Session:
    """ Behandla dela cb för månader med lösa CB rader"""
    print("Dela enligt CB")
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    cbs = local_session.query(FakturaRad_dbo.faktura_year,
                              FakturaRad_dbo.faktura_month,
                              FakturaRad_dbo.tjanst,
                              func.sum(FakturaRad_dbo.pris).label("pris_sum"),
                              func.sum(FakturaRad_dbo.antal).label("antal_sum"),
                              func.sum(FakturaRad_dbo.summa).label("summa_sum")
                              ).group_by(FakturaRad_dbo.tjanst,
                                         FakturaRad_dbo.faktura_year,
                                         FakturaRad_dbo.faktura_month
                                         ).filter(FakturaRad_dbo.tjanst.contains("Chromebook")
                                                  ).all()
    for cb in cbs:
        print(cb)
        cb_sum_rows = local_session.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.faktura_year == cb.faktura_year,
                                                                      FakturaRad_dbo.faktura_month == cb.faktura_month,
                                                                      FakturaRad_dbo.tjanst == cb.tjanst)
                                                                 ).first()
        if cb_sum_rows is None:
            FakturaRad_dbo(faktura_year=cb.faktura_year,
                           faktura_month=cb.faktura_month,
                           tjanst=cb.tjanst,
                           pris=cb.pris_sum,
                           antal=cb.antal_sum,
                           summa=cb.summa_sum,
                           split_done=True)
            local_session.commit()
        else:
            cb_sum_rows.pris = cb.pris_sum
            cb_sum_rows.antal = cb.antal_sum
            cb_sum_rows.summa = cb.summa_sum
            local_session.commit()

    # sätt alla CB rader till split_done
    local_session.query(FakturaRad_dbo).filter(FakturaRad_dbo.tjanst.contains("Chromebook")).all()
    for cb in cbs:
        cb.split_done = True
    local_session.commit()

    return local_session


def dela_enl_total_tjf(faktura_rad: FakturaRad_dbo, session: Session) -> None:
    """ Split på total tjf """
    print(f"Dela_enl_total_tjf start")


# @cache
def generate_total_tjf_for_month(month: int, session: Session = None) -> dict[str:dict[str, float]] | tuple[dict[str:dict[str, float]], Session]:
    """ sum and create a proportion for each tjanstcode in a month """
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    id_komplement_pas_aktivitet_combos = local_session.query(Tjf_dbo.id_komplement_pa, Tjf_dbo.aktivitet).distinct().all()
    try:
        return process_tjf_totals(combo_list=id_komplement_pas_aktivitet_combos, month=month, session=local_session)
    except ValueError as error:
        for id_komplement_pa, aktivitet in id_komplement_pas_aktivitet_combos:
            if aktivitet is None:
                print(f"id_komplement_pa: {id_komplement_pa}, aktivitet: {aktivitet}")
        raise ValueError from error


def process_tjf_totals(combo_list: list[list[str]], month: int, session: Session = None) -> dict[str:dict[str, float]] | tuple[dict[str:dict[str, float]], Session]:
    """ process tjf """
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    abs_total_tjf = {}
    abs_sum_tjf = 0
    MONTHS = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "maj", 6: "jun", 7: "jul", 8: "aug", 9: "sep", 10: "okt", 11: "nov", 12: "dec"}
    for id_komplement_pa, aktivitet in combo_list:
        if aktivitet is None:
            raise ValueError("There are empty numeric aktivitet in tjf")
    tjfs = local_session.query(Tjf_dbo).filter(and_(Tjf_dbo.id_komplement_pa == id_komplement_pa,
                                                    Tjf_dbo.id_komplement_pa == aktivitet)).all()
    combo_tjf_sum = 0
    for tjf in tjfs:
        combo_tjf_sum += getattr(tjf, MONTHS[month])
        abs_sum_tjf += getattr(tjf, MONTHS[month])
    abs_total_tjf[id_komplement_pa] = {aktivitet: combo_tjf_sum}
    rel_tjf = {}
    for id_komplement_pa, aktivitet in combo_list:
        rel_tjf[id_komplement_pa][aktivitet] = abs_total_tjf[id_komplement_pa][aktivitet] / abs_sum_tjf
    return rel_tjf, local_session


@cache
def gen_split_numbers_by_elevantal(enheter: set[str] = None, month: int = None, ) -> Session:
    """ generate split by elevantal """
    _, rel_split = count_student(endast_id_komplement_pa=enheter, month=month)
    return rel_split


if __name__ == "__main__":
    # gen_split_by_elevantal(enheter=["654300", "654400"])
    # generate_total_tjf_for_month(1)
    behandla_dela_cb()
    # split_row()

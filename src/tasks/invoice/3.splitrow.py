""" Hanterar uppdelning av fakturarader """
from typing import Union

from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import and_

from database.models import FakturaRad_dbo, SplitMethods_dbo, Tjf_dbo
from database.mysql_db import init_db
from utils.intergration_utils.obsidian import extract_variable_value_from_gear_name


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
    # local_session = copy_unique_tjanst(session=local_session)
    known_splits = local_session.query(SplitMethods_dbo).filter(SplitMethods_dbo.method_to_use != None).all()
    for split in known_splits:
        print(f"splitting on {split.tjanst},with method:  {split.method_to_use}")
        eval(split.method_to_use)(tjanst=split.tjanst, session=local_session)


def dela_enl_obsidian(tjanst: str, session: Session = None) -> None:
    """ split på datat i obsidian"""
    print(f"splitting on {tjanst},with method:  {dela_enl_obsidian.__name__}")
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    faktura_rader = local_session.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst == tjanst,
                                                                    FakturaRad_dbo.split_done == None)).limit(5).all()
    for faktura_rad in faktura_rader:
        kontering = extract_variable_value_from_gear_name(faktura_rad.avser, variable_name="kontering")
        print(f"{faktura_rad.avser}, kontering: {kontering}")
        eval(kontering)(faktura_rad, session=local_session)


def dela_enl_total_tjf(faktura_rad: FakturaRad_dbo, session: Session) -> None:
    """ split på total tjf """
    print(faktura_rad)


# @cache
def generate_total_tjf_for_month(month: int, session: Session = None) -> Union[dict[str:dict[str, float]], tuple[dict[str:dict[str, float]], Session]]:
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


def process_tjf_totals(combo_list: list[list[str]], month: int, session: Session = None) -> Union[dict[str:dict[str, float]], tuple[dict[str:dict[str, float]], Session]]:
    """ process tjf """
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    abs_total_tjf = {}
    abs_sum_tjf = 0
    MONTHS = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "maj", 6: "jun",
              7: "jul", 8: "aug", 9: "sep", 10: "okt", 11: "nov", 12: "dec"}
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


if __name__ == "__main__":
    generate_total_tjf_for_month(1)
    # split_row()

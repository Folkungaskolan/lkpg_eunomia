""" Fakturadelning utifrån en grupp av personer """
from sqlalchemy import and_

from database.models import Tjf_dbo
from database.mysql_db import MysqlDb

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


if __name__ == '__main__':
    pass
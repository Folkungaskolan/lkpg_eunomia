""" Hanterar uppdelning av fakturarader """
from functools import cache

from sqlalchemy import func, or_
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import and_

from database.models import FakturaRad_dbo, SplitMethods_dbo, Tjf_dbo, FakturaRadSplit_dbo
from database.mysql_db import init_db
from utils.print_progress_bar import print_progress_bar
from utils.student.count_students import count_student, generate_split_on_student_count
from utils.intergration_utils.obsidian import extract_variable_value_from_gear_name
from sqlalchemy import update

GY_AKTIVITER = {"p": "410200", "e": "410600", "a": "410500"}
GRU_AKTIVITER = {"p": "310200", "e": "310600", "a": "310500"}

ID_AKTIVITET = {"655119": GY_AKTIVITER,
                "655123": GY_AKTIVITER,
                "655122": GY_AKTIVITER,}# TODO Fortsätt här


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


def create_split_row_for_cb(year: int, month: int, total_to_split: float, split: list[str:float], session: Session = None) -> None:
    """ Mata in Chromebook fördelningen för givet år och månad """
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    for key, value in split.items():
        local_session.add(FakturaRadSplit_dbo(faktura_year=year,
                                              faktura_month=month,
                                              tjanst="Chromebook",
                                              pris=value,
                                              antal=0,
                                              summa=0))
        local_session.commit()
    return local_session


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
                                         ).filter(and_(FakturaRad_dbo.tjanst.contains("Chromebook"),
                                                       FakturaRad_dbo.faktura_month > 6
                                                       )
                                                  ).all()
    for cb in cbs:
        # Skapa en summerings referens
        month_CB_sum = local_session.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst == "Chromebook summa"),
                                                                  FakturaRad_dbo.faktura_year == cb.faktura_year,
                                                                  FakturaRad_dbo.faktura_month == cb.faktura_month
                                                                  ).first()
        if month_CB_sum is None:
            month_CB_sum = FakturaRad_dbo()
            month_CB_sum.faktura_year = cb.faktura_year
            month_CB_sum.faktura_month = cb.faktura_month
            month_CB_sum.tjanst = "Chromebook summa"
            month_CB_sum.pris = cb.pris_sum
            month_CB_sum.antal = cb.antal_sum
            month_CB_sum.summa = cb.summa_sum
            month_CB_sum.split_done = True
            month_CB_sum.split_method_used = "CB"
            local_session.add(month_CB_sum)
        else:
            month_CB_sum.faktura_year = cb.faktura_year
            month_CB_sum.faktura_month = cb.faktura_month
            month_CB_sum.tjanst = "Chromebook summa"
            month_CB_sum.pris = cb.pris_sum
            month_CB_sum.antal = cb.antal_sum
            month_CB_sum.summa = cb.summa_sum
            month_CB_sum.split_done = True
            month_CB_sum.split_method_used = "CB"
        local_session.commit()
        # Skapa en split referens
        split_by_student = generate_split_on_student_count(year=cb.year,
                                                           month=cb.faktura_month,
                                                           enheter_to_split_over={"CB"},
                                                           session=local_session
                                                           )
        # Skapa en delning
        for enhet, enhets_andel in split_by_student.items():
            local_session.add(FakturaRadSplit_dbo(faktura_year=cb.faktura_year,
                                                  faktura_month=cb.faktura_month,
                                                  tjanst="Chromebook",
                                                  split_summa=enhets_andel * cb.pris_sum,
                                                  aktivitet=
                                                  summa = 0))
            local_session.commit()
            local_session = create_split_row_for_cb(year=cb.faktura_year,
                                                    month=FakturaRad_dbo.faktura_month,
                                                    total_to_split=cb.summa_sum,
                                                    split=generate_split_on_student_count(month=cb.faktura_month),
                                                    session=local_session)

        # sätt alla CB rader till split_done
        cbs = local_session.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst.contains("Chromebook"),
                                                              FakturaRad_dbo.tjanst != "Chromebook summa",
                                                              FakturaRad_dbo.split_done == 0
                                                              )
                                                         ).all()

        for cb in cbs:
            cb.split_done = 1
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

        def process_tjf_totals(combo_list: list[list[str]], month: int, session: Session = None) -> dict[str:dict[str, float]] | tuple[
            dict[str:dict[str, float]], Session]:
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

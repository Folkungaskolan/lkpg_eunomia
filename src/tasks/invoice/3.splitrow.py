""" Hanterar uppdelning av fakturarader """
from functools import cache

from sqlalchemy import func, or_
from sqlalchemy.sql.elements import and_

from CustomErrors import GearNotFoundInFASIT_CBAError, GearNotAssignedToAUserError, NoKonteringSetInFasit, DelaInteEnligDennaMetod, NoUserFoundError
from database.models import FakturaRad_dbo, Tjf_dbo, FakturaRadSplit_dbo, FasitCopy, Staff_dbo, TjanstKategori_dbo
from database.mysql_db import MysqlDb
from settings.enhetsinfo import ID_AKTIVITET

from utils.dbutil.fasit_db import get_user_id_for_fasit_user, get_fasit_row
from utils.dbutil.staff_db import gen_tjf_for_staff, get_tjf_for_enhet
from utils.dbutil.student_db import generate_split_on_student_count
from utils.faktura_utils.kontering import decode_kontering_in_fritext
from utils.faktura_utils.print_table import print_headers, print_row, COL_WIDTHS
from utils.flatten import flatten_row
from utils.print_progress_bar import print_progress_bar

from utils.intergration_utils.obsidian import extract_variable_value_from_gear_name
from utils.student.student_mysql import count_student


def dela_enl_fasit_agare(faktura_rad: FakturaRad_dbo, verbose: bool = False) -> (bool, str):
    """ Dela enligt fasit ägare
    returnerar

    Falskt om det inte går att dela på fasit ägare
    Sant om metoden fungerade

    om det ör någon ändring på metod kommer det tillbaka som en sträng
    """
    split_metod = "fasit_ägare"
    if verbose: print(f"Dela_enl_fasit_ägare start                  2022-11-21 12:34:00")
    s = MysqlDb().session()
    fasit_rad = s.query(FasitCopy).filter(FasitCopy.name == faktura_rad.avser).first()
    if fasit_rad is None or fasit_rad.attribute_anvandare is None or len(fasit_rad.attribute_anvandare) < 2:
        # raden finns inte i fasit, exv ärenden
        #                     eller är inte kopplad till en användare
        #                                                                eller är kopplad till en med för kort namn
        #                                                                                                             mina ska alltid gå till konterings kontroll
        return False
    else:
        if verbose: print(f"{fasit_rad.attribute_anvandare:},                            2022-11-21 12:35:30")
        try:
            user_id = get_user_id_for_fasit_user(fasit_rad.attribute_anvandare)
        except NoUserFoundError:
            return False
        user_aktivitet_char = s.query(Staff_dbo.aktivitet_char).filter(Staff_dbo.id == user_id).first()
        if user_aktivitet_char is None:
            return False
        bibliotekarier = flatten_row(s.query(Staff_dbo.user_id).filter(Staff_dbo.titel.startswith("Biblio").all()))
        janitors = flatten_row(s.query(Staff_dbo.user_id).filter(Staff_dbo.titel.startswith("Vaktm").all()))
        if user_id in bibliotekarier:  # ["tinasp", "magbro"]:  # bibliotekets kostnader går över hela skolan
            split = generate_split_on_student_count(enheter=["656", "655"],  # Delas över Gymnasiet
                                                    month=faktura_rad.faktura_month,
                                                    year=faktura_rad.faktura_year)
            split_metod = "Kontering>FolkungaBibliotek"
        elif user_id in janitors:  # ["jonbjc", "kenchr"]:  # vaktmästarnas kostnader går över hela skolan
            split = generate_split_on_student_count(enheter=["656", "655"],  # Delas över Gymnasiet
                                                    month=faktura_rad.faktura_month,
                                                    year=faktura_rad.faktura_year)
            split_metod = "Kontering>Vaktmästare"
        elif user_id == "lyadol":
            if "Personlig utr" not in fasit_rad.eunomia_kontering:
                split = generate_split_on_student_count(enheter=["656", "655"],  # Delas över Gymnasiet
                                                    month=faktura_rad.faktura_month,
                                                    year=faktura_rad.faktura_year)
                split_metod = "Kontering>IT-Tekniker Buffert"
            else:
                split = gen_tjf_for_staff(user_id=user_id, rad=faktura_rad)
                split_metod = "Kontering>IT-Tekniker Personlig utr"
        else:
            split = gen_tjf_for_staff(user_id=user_id, rad=faktura_rad)

        for enhet, enhet_andel in split:
            s.add(FakturaRadSplit_dbo(
                faktura_year=faktura_rad.faktura_year,
                faktura_month=faktura_rad.faktura_month,
                tjanst=faktura_rad.tjanst,
                split_summa=enhet_andel * faktura_rad.summa,
                id_komplement_pa=enhet,
                aktivitet=ID_AKTIVITET[enhet][user_aktivitet_char]
            ))
        faktura_rad.split_done = 1
        faktura_rad.split_method = split_metod
        s.commit()
        return True


def dela_enl_fasit_kontering(faktura_rad:, verbose: bool = False) -> bool:
    """ dela enligt fasit kontering """
    if verbose: print(f"Dela_enl_fasit_kontering start                         2022-11-21 12:55:46")
    s = MysqlDb().session()
    fasit_rad = s.query(FasitCopy).filter(FasitCopy.name == faktura_rad.avser).first()
    if fasit_rad is None or fasit_rad.eunomia_kontering is None or len(fasit_rad.eunomia_kontering) == 0:
        return False
    else:
        if verbose: print(f"{fasit_rad.eunomia_kontering:},                            2022-11-21 12:56:24")
        kontering, aktivitet_char, metod_string = decode_kontering_in_fritext(faktura_rad=faktura_rad,
                                                                              fasit_rad=fasit_rad)
        for enhet in kontering.keys():
            s.add(FakturaRadSplit_dbo(
                faktura_year=faktura_rad.faktura_year,
                faktura_month=faktura_rad.faktura_month,
                tjanst=faktura_rad.tjanst,
                avser=faktura_rad.avser,
                split_summa=kontering[enhet] * faktura_rad.summa,
                id_komplement_pa=enhet,
                aktivitet=ID_AKTIVITET[enhet][aktivitet_char]
            ))
        faktura_rad.split_done = 1
        if metod_string is None:
            faktura_rad.split_method = "fasit_kontering"
        else:
            faktura_rad.split_method = metod_string
    s.commit()
    return False


def dela_enligt_total_tjf(faktura_rad, dela_over_enheter: list[str], verbose: bool = False) -> None:
    """ Dela enligt total tjf
    dela_over_enheter är en lista med enheter som ska delas över
    """
    print(F"bu")  # TODO 2022-11-23 17:13:38
    split = get_tjf_for_enhet(enheter=dela_over_enheter, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year, verbose=verbose)
    return gen_split_rows(faktura_rad=faktura_rad, split=split, aktivitet_char="p", split_method="elevantal")


def dela_enligt_elevantal(faktura_rad: FakturaRad_dbo, dela_over_enheter: list[str]) -> bool:
    """ Dela enligt elevantal """
    s = MysqlDb().session()
    split = generate_split_on_student_count(enheter=dela_over_enheter, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
    # aktivitet_char                                                                                     "p"  # TODO blir detta rätt Fråga Maria H
    return gen_split_rows(faktura_rad=faktura_rad, split=split, aktivitet_char="p", split_method="elevantal")


def gen_split_rows(faktura_rad: FakturaRad_dbo,
                   split: list[str:float],
                   aktivitet_char: str,
                   split_method: str = "unknown") -> bool:
    """ generera split raderna """
    s = MysqlDb().session()
    for enhet in split.keys():
        s.add(FakturaRadSplit_dbo(
            split_id=faktura_rad.id,
            faktura_year=faktura_rad.faktura_year,
            faktura_month=faktura_rad.faktura_month,
            tjanst=faktura_rad.tjanst,
            avser=faktura_rad.avser,
            split_method=split_method,
            split_summa=split[enhet] * faktura_rad.summa,
            id_komplement_pa=enhet,
            aktivitet=ID_AKTIVITET[enhet][aktivitet_char]
        ))
    faktura_rad.split_done = 1
    faktura_rad.split_method = split_method
    s.commit()
    return True


def split_row(months: list[str] = None, verbose: bool = False) -> None:
    """ split row """
    s = MysqlDb().session()
    # behandla_dela_cb()
    if months is None:
        rader = s.query(FakturaRad_dbo).filter(or_(FakturaRad_dbo.split_done == None,
                                                   FakturaRad_dbo.split_done == 0)
                                               ).all()
        # ).limit(2).all()
    else:
        rader = s.query(FakturaRad_dbo).filter(and_(or_(FakturaRad_dbo.split_done == None,
                                                        FakturaRad_dbo.split_done == 0),
                                                    FakturaRad_dbo.faktura_year == 2022,
                                                    FakturaRad_dbo.faktura_month.in_(months)
                                                    )
                                               ).all()
        # ).limit(2).all()
    fasit_kontering_successful = False  # säkerställer att värden finns för när utskriftgen sker
    tot_tjf_successful = False
    elevantal_successful = False
    print_headers()
    for faktura_rad in rader:
        # print(rad)
        if verbose: print("Dela enligt Fasit ägare                             2022-11-21 12:33:22")
        fasit_kontering_successful = dela_enl_fasit_kontering(faktura_rad)
        if not fasit_kontering_successful:
            fasit_agare_successful, metod = dela_enl_fasit_agare(faktura_rad)
            if not fasit_agare_successful:
                fasit_rad = get_fasit_row(name=faktura_rad.avser)
                if faktura_rad.fakturamarkning.startswith("S:t Lars"):
                    dela_over_enheter = ["654"]
                elif faktura_rad.fakturamarkning.startswith("Folkungaskolan"):
                    dela_over_enheter = ["656", "655"]
                else:
                    raise Exception("Unknown fakturamarkning                              2022-11-22 15:16:18")
            if fasit_rad.tag_anknytning == 1 \
                    or fasit_rad.tag_rcard == 1 \
                    or fasit_rad.tag_mobiltelefon == 1 \
                    or fasit_rad.tag_skrivare == 1:
                tot_tjf_successful = dela_enligt_total_tjf(faktura_rad, dela_over_enheter=dela_over_enheter)
            elif fasit_rad.tag_chromebox == 1 \
                    or fasit_rad.tag_domain == 1 \
                    or fasit_rad.tag_videoprojektor == 1 \
                    or fasit_rad.tag_funktionskonto == 1:
                elevantal_successful = dela_enligt_elevantal(faktura_rad, dela_over_enheter=dela_over_enheter)

        if not fasit_agare_successful and not fasit_kontering_successful and not tot_tjf_successful:
            print_row(row_values={"Period": F"{faktura_rad.faktura_year}-{faktura_rad.faktura_month}",
                                  "Tjänst": faktura_rad.tjanst[:[COL_WIDTHS["Tjänst"]]],
                                  "Avser": faktura_rad.avser[:[COL_WIDTHS["Avser"]]],
                                  "Summa": faktura_rad.summa[:[COL_WIDTHS["Summa"]]],
                                  "Fasit ägare": fasit_agare_successful,
                                  "Fasit kontering": fasit_kontering_successful,
                                  "Tot Tjf": tot_tjf_successful,
                                  "Elevantal": elevantal_successful,
                                  "Summary": "Failed"})
        else:
            print_row(row_values={"Period": F"{faktura_rad.faktura_year}-{faktura_rad.faktura_month}",
                                  "Tjänst": faktura_rad.tjanst[:[COL_WIDTHS["Tjänst"]]],
                                  "Avser": faktura_rad.avser[:[COL_WIDTHS["Avser"]]],
                                  "Summa": faktura_rad.summa[:[COL_WIDTHS["Summa"]]],
                                  "Fasit ägare": fasit_agare_successful,
                                  "Fasit kontering": fasit_kontering_successful,
                                  "Tot Tjf": tot_tjf_successful,
                                  "Elevantal": elevantal_successful,
                                  "Summary": "Success"})


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


def behandla_dela_cb(verbose: bool = False) -> None:
    """ Behandla dela cb för månader med lösa CB rader"""
    if verbose: print("Dela enligt CB")
    s = MysqlDb().session()
    sum_cbs = s.query(FakturaRad_dbo.id,
                      FakturaRad_dbo.faktura_year,
                      FakturaRad_dbo.faktura_month,
                      FakturaRad_dbo.tjanst,
                      func.sum(FakturaRad_dbo.pris).label("pris_sum"),
                      func.sum(FakturaRad_dbo.antal).label("antal_sum"),
                      func.sum(FakturaRad_dbo.summa).label("summa_sum")
                      ).group_by(FakturaRad_dbo.tjanst,
                                 FakturaRad_dbo.faktura_year,
                                 FakturaRad_dbo.faktura_month
                                 ).filter(and_(FakturaRad_dbo.tjanst.contains("Chromebook"),
                                               FakturaRad_dbo.faktura_month > 6,
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
            month_CB_sum = FakturaRad_dbo()
            month_CB_sum.faktura_year = sum_cb.faktura_year
            month_CB_sum.faktura_month = sum_cb.faktura_month
            month_CB_sum.tjanst = "Chromebook summa"
            month_CB_sum.pris = sum_cb.pris_sum / sum_cb.antal_sum
            month_CB_sum.antal = sum_cb.antal_sum
            month_CB_sum.split_summa = sum_cb.summa_sum
            month_CB_sum.split_done = True
            month_CB_sum.split_method_used = "CB"
            s.add(month_CB_sum)
        else:
            month_CB_sum.faktura_year = sum_cb.faktura_year
            month_CB_sum.faktura_month = sum_cb.faktura_month
            month_CB_sum.tjanst = "Chromebook summa"
            month_CB_sum.pris = int(sum_cb.pris_sum / float(sum_cb.antal_sum))
            month_CB_sum.antal = sum_cb.antal_sum
            month_CB_sum.split_summa = sum_cb.summa_sum
            month_CB_sum.split_done = True
            month_CB_sum.split_method_used = "CB"
        s.commit()
        # Skapa en split referens
        split_by_student = generate_split_on_student_count(year=sum_cb.faktura_year,
                                                           month=sum_cb.faktura_month,
                                                           enheter_to_split_over={"CB"}
                                                           )
        if sum(split_by_student.values()) != 1:  # sum(split_by_student.values()) ska summera till 1 annars har vi fel
            raise ValueError(f"Summan av split_by_student ska vara 1 men är {sum(split_by_student.values())}")
        # Skapa en delning
        for enhet, enhets_andel in split_by_student.items():
            split_row = s.query(FakturaRadSplit_dbo).filter(and_(FakturaRadSplit_dbo.faktura_year == sum_cb.faktura_year,
                                                                 FakturaRadSplit_dbo.faktura_month == sum_cb.faktura_month,
                                                                 FakturaRadSplit_dbo.tjanst == "Chromebooks",
                                                                 FakturaRadSplit_dbo.id_komplement_pa == enhet,
                                                                 FakturaRadSplit_dbo.aktivitet == ID_AKTIVITET[enhet]["p"]
                                                                 )).first()
            if split_row is None:
                if verbose: print(
                    f"uppdaterar split rad för {enhet} ID_AKTIVITET[enhet]['p'] {ID_AKTIVITET[enhet]['p']} | {enhets_andel:2f} * {sum_cb.pris_sum:2f} = {enhets_andel * sum_cb.pris_sum:2f}")
                s.add(FakturaRadSplit_dbo(faktura_year=sum_cb.faktura_year,
                                          faktura_month=sum_cb.faktura_month,
                                          split_id=666,  # CB kommer ha backreferens till summerings raden TODO
                                          tjanst="Chromebooks",
                                          avser="Chromebooks",
                                          anvandare="Chromebooks",
                                          id_komplement_pa=enhet,
                                          split_summa=enhets_andel * sum_cb.pris_sum,
                                          aktivitet=ID_AKTIVITET[enhet]["p"]
                                          )
                      )
            else:
                # split_row.year, month, id_komplement_pa, aktivtet # är redan rätt om den hittats
                if verbose: print(
                    f"uppdaterar split rad för {enhet} ID_AKTIVITET[enhet]['p'] {ID_AKTIVITET[enhet]['p']} | {enhets_andel:2f} * {sum_cb.pris_sum:2f} = {enhets_andel * sum_cb.pris_sum:2f}")
                split_row.split_summa = enhets_andel * sum_cb.pris_sum
        s.commit()

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


def copy_distinct_tjansts_to_tjanst_kategorisering():
    """ för gruppering i Pivot """
    s = MysqlDb().session()
    tjfs = s.query(FakturaRad_dbo.tjanst).distinct().all()
    for t in tjfs:
        tjanst_rad = s.query(TjanstKategori_dbo).filter(TjanstKategori_dbo.tjanst == t).first()
        if tjanst_rad is None:
            s.add(TjanstKategori_dbo(tjanst=t))
        else:
            continue
    s.commit()


if __name__ == "__main__":
    # gen_split_by_elevantal(enheter=["654300", "654400"])
    # generate_total_tjf_for_month(1)
    # behandla_dela_cb()
    split_row(months=["7", "8", "9", "10", "11", "12"])

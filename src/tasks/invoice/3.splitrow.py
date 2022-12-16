""" Hanterar uppdelning av fakturarader """
import inspect

from sqlalchemy import func, or_
from sqlalchemy.sql.elements import and_

from CustomErrors import NoUserFoundError, ExtrapolationError
from database.models import FakturaRad_dbo, Tjf_dbo, FakturaRadSplit_dbo, FasitCopy, Staff_dbo
from database.mysql_db import MysqlDb
from settings.enhetsinfo import ID_AKTIVITET
from utils.EunomiaEnums import EnhetsAggregering, FakturaRadState
from utils.dbutil.fasit_db import get_user_id_for_fasit_user, get_fasit_row
from utils.dbutil.kategori_db import get_kategorier_for
from utils.dbutil.staff_db import gen_tjf_for_staff, get_tjf_for_enhet
from utils.dbutil.student_db import calc_split_on_student_count
from utils.faktura_utils.kontering import decode_kontering_in_fritext
from utils.faktura_utils.print_table import print_headers, COL_WIDTHS, print_start, print_result
from utils.faktura_utils.reset_rows import reset_faktura_row_id
from utils.flatten import flatten_row


def dela_enl_fasit_agare(faktura_rad: FakturaRad_dbo, verbose: bool = False) -> (FakturaRadState, str):
    """ Dela enligt fasit ägare
    returnerar

    Falskt om det inte går att dela på fasit ägare
    Sant om metoden fungerade

    om det ör någon ändring på metod kommer det tillbaka som en sträng
    """
    split_method = "fasit_ägare"
    if verbose: print(f"Dela_enl_fasit_ägare start                  2022-11-21 12:34:00")
    s = MysqlDb().session()
    fasit_rad = s.query(FasitCopy).filter(FasitCopy.name == faktura_rad.avser).first()
    if fasit_rad is None or fasit_rad.attribute_anvandare is None or len(fasit_rad.attribute_anvandare) < 2:
        # raden finns inte i fasit, exv ärenden
        #                     eller är inte kopplad till en användare
        #                                                                eller är kopplad till en med för kort namn
        #                                                                                                             mina ska alltid gå till konterings kontroll
        return FakturaRadState.SPLIT_INCOMPLETE, "dela_enl_fasit_agare ->  fasit_rad is None "
    else:
        if verbose:
            print(f"{fasit_rad.attribute_anvandare:},                            2022-11-21 12:35:30")
        try:
            user_id = get_user_id_for_fasit_user(fasit_rad.attribute_anvandare)
        except NoUserFoundError:
            return FakturaRadState.SPLIT_INCOMPLETE, "dela_enl_fasit_agare -> NoUserFoundError"
        user_aktivitet_char = s.query(Staff_dbo.aktivitet_char).filter(Staff_dbo.user_id == user_id).first()[0]
        if user_aktivitet_char is None:
            return FakturaRadState.SPLIT_INCOMPLETE, "dela_enl_fasit_agare -> user_aktivitet_char is None"
        bibliotekarier = flatten_row(s.query(Staff_dbo.user_id).filter(Staff_dbo.titel.startswith("Biblio")).all())
        janitors = flatten_row(s.query(Staff_dbo.user_id).filter(Staff_dbo.titel.startswith("Vaktm")).all())
        if user_id in bibliotekarier:  # ["tinasp", "magbro"]:  # bibliotekets kostnader går över hela skolan
            split = calc_split_on_student_count(enheter_to_split_over=["656", "655"],  # Delas över Gymnasiet
                                                month=faktura_rad.faktura_month,
                                                year=faktura_rad.faktura_year)
            split_method = "Kontering>FolkungaBibliotek"
        elif user_id in janitors:  # ["jonbjc", "kenchr"]:  # vaktmästarnas kostnader går över hela skolan
            split = calc_split_on_student_count(enheter_to_split_over=["656", "655"],  # Delas över Gymnasiet
                                                month=faktura_rad.faktura_month,
                                                year=faktura_rad.faktura_year)
            split_method = "Kontering>Vaktmästare"
        elif user_id in "viklun":
            split = calc_split_on_student_count(enheter_to_split_over=[EnhetsAggregering.GRU7_9],
                                                month=faktura_rad.faktura_month,
                                                year=faktura_rad.faktura_year)
            split_method = "Kontering>tf syv"
        elif user_id == "lyadol":
            if fasit_rad.eunomia_kontering is None or "Personlig utr" not in fasit_rad.eunomia_kontering:
                split = calc_split_on_student_count(enheter_to_split_over=["656", "655"],
                                                    month=faktura_rad.faktura_month,
                                                    year=faktura_rad.faktura_year)
                split_method = "Kontering>IT-Tekniker Buffert"
                user_aktivitet_char = "p"  # Min buffert ska gå som pedagogisk kostnad
            else:
                split = gen_tjf_for_staff(user_id=user_id, month_nr=faktura_rad.faktura_month)
                split_method = "Kontering>IT-Tekniker Personlig utr"
        else:
            try:
                split = gen_tjf_for_staff(user_id=user_id, month_nr=faktura_rad.faktura_month)
            except ExtrapolationError:
                split = get_tjf_for_enhet(enheter=faktura_rad.dela_over_enheter, month=faktura_rad.faktura_month)
                return FakturaRadState.SPLIT_BY_GENERELL_TFJ_SUCCESSFUL, "Delad enligt gen tjf -> ExtrapolationError för användaren"

        result_bool_successful: bool = insert_split_into_database(faktura_rad=faktura_rad, split=split, aktivitet_char=user_aktivitet_char, split_method=split_method)
        if result_bool_successful:
            faktura_rad.split_done = 1
            faktura_rad.split_method = split_method
        s.commit()
        return FakturaRadState.SPLIT_BY_FASIT_USER_SUCCESSFUL, split_method


def dela_enl_fasit_kontering(*, faktura_rad: FakturaRad_dbo, verbose: bool = False, manuell_kontering: str = None, notering: str = None) -> tuple[FakturaRadState, str]:
    """ Dela enligt fasit kontering
    :param notering:        :type str:  läggs längst bak i konteringen som information till sammanställningen
    :param verbose:         :type bool: vill du att stack information ska skrivas ut
    :param faktura_rad:     :type faktura_rad: faktura objektet som ska delas
    :type manuell_kontering :type str :  med manuell kontering i formatet  "Kontering>Elevantal<656;655|aktivitet:p"
    """
    if verbose:
        print(f"Dela_enl_fasit_kontering start                         2022-11-21 12:55:46")
    s = MysqlDb().session()
    fasit_rad = s.query(FasitCopy).filter(FasitCopy.name == faktura_rad.avser).first()
    if fasit_rad is None or fasit_rad.eunomia_kontering is None or len(fasit_rad.eunomia_kontering) == 0:
        return FakturaRadState.SPLIT_INCOMPLETE, "Fail dela_enl_fasit_kontering fail no kontering in fasit"
    else:
        if verbose:
            print(f"{fasit_rad.eunomia_kontering:},                            2022-11-21 12:56:24")
        if manuell_kontering is None:
            split, aktivitet_char, metod_string = decode_kontering_in_fritext(faktura_rad=faktura_rad,
                                                                              konterings_string=fasit_rad.eunomia_kontering)
        else:
            split, aktivitet_char, metod_string = decode_kontering_in_fritext(faktura_rad=faktura_rad,
                                                                              konterings_string=F"Manuell kontering: {manuell_kontering}")
        if metod_string is False:  # betyder att vi inte ska köra på fasit kontering för denna rad, trots att det finns konterings info
            return FakturaRadState.SPLIT_INCOMPLETE, "Fail dela_enl_fasit_kontering fail no kontering in fasit"
        success = insert_split_into_database(faktura_rad=faktura_rad,
                                             split=split,
                                             aktivitet_char=aktivitet_char,
                                             split_method=F"{metod_string}|{notering}")
        if success:
            return FakturaRadState.SPLIT_BY_FASIT_KONTERING_SUCCESSFUL, metod_string
        else:
            return FakturaRadState.SPLIT_INCOMPLETE, "Fail dela_enl_fasit_kontering fail no kontering in fasit"


def insert_split_into_database(*, faktura_rad: FakturaRad_dbo, split: dict[str, float], aktivitet_char: str, split_method: str = "unknown") -> bool:
    """ generera split raderna """
    s = MysqlDb().session()
    for enhet in split.keys():
        if split[enhet] == 0:  # vi sparar inte noll rader
            continue
        old = s.query(FakturaRadSplit_dbo).filter(and_(FakturaRadSplit_dbo.faktura_year == faktura_rad.faktura_year,
                                                       FakturaRadSplit_dbo.faktura_month == faktura_rad.faktura_month,
                                                       FakturaRadSplit_dbo.id_komplement_pa == enhet,
                                                       FakturaRadSplit_dbo.split_id == faktura_rad.id)
                                                  ).first()
        if old is not None:
            old.anvandare = faktura_rad.anvandare
            old.avser = faktura_rad.avser
            old.tjanst = faktura_rad.tjanst
            old.split_summa = split[enhet] * faktura_rad.summa
            old.split_metod = split_method
            old.aktivitet = ID_AKTIVITET[enhet][aktivitet_char]
            old.tjanst_kategori_lvl1, old.tjanst_kategori_lvl2 = get_kategorier_for(tjanst=faktura_rad.tjanst)

        else:
            new = FakturaRadSplit_dbo(
                split_id=faktura_rad.id,
                faktura_year=faktura_rad.faktura_year,
                faktura_month=faktura_rad.faktura_month,
                tjanst=faktura_rad.tjanst,
                avser=faktura_rad.avser,
                anvandare=faktura_rad.anvandare,
                split_method_used=split_method,
                split_summa=split[enhet] * faktura_rad.summa,
                id_komplement_pa=enhet,
                aktivitet=ID_AKTIVITET[enhet][aktivitet_char])
            new.tjanst_kategori_lvl1, new.tjanst_kategori_lvl2 = get_kategorier_for(tjanst=faktura_rad.tjanst)
            s.add(new)
        s.commit()
    faktura_rad.split_done = 1
    faktura_rad.split_method_used = split_method
    s.commit()
    return True


def split_row(months: list[str] = None, verbose: bool = False, avser: str = None, row_ids: list[int] = None) -> None:
    """ split row """
    s = MysqlDb().session()
    if avser is None and row_ids is None:
        behandla_dela_cb()

    if avser is not None:
        rader = s.query(FakturaRad_dbo).filter(and_(or_(FakturaRad_dbo.split_done == None,
                                                        FakturaRad_dbo.split_done == 0),
                                                    FakturaRad_dbo.faktura_year == 2022,
                                                    FakturaRad_dbo.faktura_month.in_(months),
                                                    FakturaRad_dbo.avser == avser
                                                    )
                                               ).all()
    elif row_ids is not None:
        rader = s.query(FakturaRad_dbo).filter(FakturaRad_dbo.id.in_(row_ids)).all()
    elif months is not None:
        rader = s.query(FakturaRad_dbo).filter(and_(or_(FakturaRad_dbo.split_done == None,
                                                        FakturaRad_dbo.split_done == 0),
                                                    FakturaRad_dbo.faktura_year == 2022,
                                                    FakturaRad_dbo.faktura_month.in_(months)
                                                    )
                                               ).all()
    else:
        rader = s.query(FakturaRad_dbo).filter(or_(FakturaRad_dbo.split_done == None,
                                                   FakturaRad_dbo.split_done == 0)
                                               ).all()

    fasit_kontering_successful = False  # säkerställer att värden finns för när utskriften sker
    tot_tjf_successful = False
    elevantal_successful = False
    print_headers()
    for faktura_rad in rader:
        print_start(row_values={"ID": faktura_rad.id,
                                "Period": F"{faktura_rad.faktura_year}-{faktura_rad.faktura_month}",
                                "Tjänst": faktura_rad.tjanst[:COL_WIDTHS["Tjänst"]],
                                "Avser": faktura_rad.avser[:COL_WIDTHS["Avser"]],
                                "Summa": faktura_rad.summa})

        if verbose:
            print("Dela enligt Fasit ägare                             2022-11-21 12:33:22")
        split_status = FakturaRadState.SPLIT_INCOMPLETE

        # Första delnings prioriteten är att dela på fasit Kontering
        split_status, split_method_string = dela_enl_fasit_kontering(faktura_rad=faktura_rad)

        # förbered generell enhet att dela raden över
        faktura_rad.dela_over_enheter = translate_school_to_general_enheter(fakturamarkning=faktura_rad.fakturamarkning)

        # Fasta delningar beroende på tjänst
        if faktura_rad.avser == "Pgm Adobe CC for EDU K12":  # A513
            split_status, split_method_string = dela_enl_fasit_kontering(faktura_rad, manuell_kontering="Kontering>Elevantal<656;655|aktivitet:p")
            split_method_string = "Pgm Adobe CC"
        if faktura_rad.avser == "E47180":  # Nya Pykologens dator
            split_status = insert_split_into_database(faktura_rad=faktura_rad,
                                                      split=calc_split_on_student_count(enheter_to_split_over=EnhetsAggregering.GRU7_9,
                                                                                        month=faktura_rad.faktura_month,
                                                                                        year=faktura_rad.faktura_year),
                                                      aktivitet_char="e",  # TODO blir detta rätt Fråga Maria H
                                                      split_method="Nya Psykologen enligt elevantal")
            continue

        # Databas beroende delningar
        if split_status == FakturaRadState.SPLIT_INCOMPLETE:
            split_status, split_method_string = dela_enl_fasit_agare(faktura_rad)
            if split_status == FakturaRadState.SPLIT_INCOMPLETE:
                fasit_rad = get_fasit_row(name=faktura_rad.avser)
                if fasit_rad is not None:
                    if fasit_rad.tag_chromebox == 1 \
                            or fasit_rad.tag_domain == 1 \
                            or fasit_rad.tag_videoprojektor == 1 \
                            or fasit_rad.tag_funktionskonto == 1:
                        insert_split_into_database(faktura_rad=faktura_rad,
                                                   split=calc_split_on_student_count(enheter_to_split_over=faktura_rad.dela_over_enheter,
                                                                                     month=faktura_rad.faktura_month,
                                                                                     year=faktura_rad.faktura_year),
                                                   aktivitet_char="p",  # TODO blir detta rätt Fråga Maria H
                                                   split_method="elevantal")
                        split_status = FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL
                        split_method_string = "elevantal"
                    elif fasit_rad.tag_anknytning == 1 \
                            or fasit_rad.tag_rcard == 1 \
                            or fasit_rad.tag_mobiltelefon == 1 \
                            or fasit_rad.tag_skrivare == 1:
                        insert_split_into_database(faktura_rad=faktura_rad,
                                                   split=get_tjf_for_enhet(enheter=faktura_rad.dela_over_enheter,
                                                                           month=faktura_rad.faktura_month),
                                                   aktivitet_char="p",
                                                   split_method="Generell tjf")
                        split_status = FakturaRadState.SPLIT_BY_GENERELL_TFJ_SUCCESSFUL
                        split_method_string = "Gererell Tjf"
                # if all else fails
                split_method_string = "Failsafe elevantal Åtgärda"
                elevantal_successful = insert_split_into_database(faktura_rad=faktura_rad,
                                                                  split=calc_split_on_student_count(enheter_to_split_over=faktura_rad.dela_over_enheter,
                                                                                                    month=faktura_rad.faktura_month,
                                                                                                    year=faktura_rad.faktura_year),
                                                                  aktivitet_char="p",  # TODO blir detta rätt Fråga Maria H
                                                                  split_method=split_method_string)

        if not split_status.value.endswith("SUCCESSFUL"):
            print_result(row_values={"Fasit ägare": split_status == FakturaRadState.SPLIT_BY_FASIT_USER_SUCCESSFUL,
                                     "Fasit kontering": split_status == FakturaRadState.SPLIT_BY_FASIT_KONTERING_SUCCESSFUL,
                                     "Tot Tjf": split_status == FakturaRadState.SPLIT_BY_GENERELL_TFJ_SUCCESSFUL,
                                     "Elevantal": split_status == FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL,
                                     "Summary": "Failed",
                                     "split_string": "-"})

        else:
            print_result(row_values={"Fasit ägare": split_status == FakturaRadState.SPLIT_BY_FASIT_USER_SUCCESSFUL,
                                     "Fasit kontering": split_status == FakturaRadState.SPLIT_BY_FASIT_KONTERING_SUCCESSFUL,
                                     "Tot Tjf": split_status == FakturaRadState.SPLIT_BY_GENERELL_TFJ_SUCCESSFUL,
                                     "Elevantal": split_status == FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL,
                                     "Summary": "Success",
                                     "split_string": split_method_string})


def translate_school_to_general_enheter(fakturamarkning) -> list[str]:
    """ Översätter från skolans namn till enheter som finns på skolan att dela över som backup om det inte finns någon fasit rad"""
    if fakturamarkning.startswith("S:t Lars"):
        return ["654"]
    elif fakturamarkning.startswith("Folkungaskolan"):
        return ["656", "655"]
    else:
        raise Exception("Unknown fakturamarkning                              2022-11-22 15:16:18")


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


def create_cb_split_rows(verbose: bool = False) -> None:
    """ Skapa split rader för CB """
    s = MysqlDb().session()

    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    sum_rows = s.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst == "Chromebook summa")).all()
    for sum_row in sum_rows:
        split_by_student = calc_split_on_student_count(year=sum_row.faktura_year,
                                                       month=sum_row.faktura_month,
                                                       enheter_to_split_over={EnhetsAggregering.CB}
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


if __name__ == "__main__":
    # gen_split_by_elevantal(enheter=["654300", "654400"])
    # generate_total_tjf_for_month(1)
    # behandla_dela_cb()

    # gear_id = "E47732"
    # reset_avser(gear_id)
    # split_row(months=["7", "8", "9", "10", "11", "12"], avser=gear_id)
    #
    row_id = [12290]
    reset_faktura_row_id(row_ids=row_id)
    split_row(row_ids=row_id)

    # split_row(months=["7", "8", "9", "10", "11", "12"])

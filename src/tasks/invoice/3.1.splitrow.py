""" Hanterar uppdelning av fakturarader """

from sqlalchemy import or_
from sqlalchemy.sql.elements import and_

from CustomErrors import NoUserFoundError, NoTjfFoundError
from database.models import FakturaRad_dbo, FasitCopy, Staff_dbo
from database.mysql_db import MysqlDb
from utils.EunomiaEnums import EnhetsAggregering, FakturaRadState, Aktivitet
from utils.dbutil.fasit_db import get_user_id_for_fasit_user, get_fasit_row
from utils.dbutil.staff_db import gen_tjf_for_staff, get_tjf_for_enhet, is_staff_old
from utils.dbutil.student_db import calc_split_on_student_count
from utils.faktura_utils.kontering import decode_kontering_in_fritext
from utils.faktura_utils.print_table import print_headers, COL_WIDTHS, print_start
from utils.faktura_utils.reset_rows import reset_faktura_row_id
from utils.flatten import flatten_row
from utils.faktura_utils.3. import dela_enl_fasit_kontering, FakturaRadState
def dela_enl_fasit_agare(faktura_rad: FakturaRad_dbo, verbose: bool = False) -> (FakturaRadState):
    """ Dela enligt fasit ägare
    returnerar

    Falskt om det inte går att dela på fasit ägare
    Sant om metoden fungerade

    om det ör någon ändring på metod kommer det tillbaka som en sträng
    """
    split_method_text = "fasit_ägare"
    if verbose: print(f"Dela_enl_fasit_ägare start                  2022-11-21 12:34:00")
    s = MysqlDb().session()
    fasit_rad = s.query(FasitCopy).filter(FasitCopy.name == faktura_rad.avser).first()
    if fasit_rad is None or fasit_rad.attribute_anvandare is None or len(fasit_rad.attribute_anvandare) < 2:
        # raden finns inte i fasit, exv ärenden
        #                     eller är inte kopplad till en användare
        #                                                                eller är kopplad till en med för kort namn
        #                                                                                                             mina ska alltid gå till konterings kontroll
        faktura_rad.split_status = FakturaRadState.SPLIT_INCOMPLETE
        faktura_rad.split_method_used = "dela_enl_fasit_agare ->  fasit_rad is None "
        return faktura_rad.split_status
    else:
        if verbose:
            print(f"{fasit_rad.attribute_anvandare:},                            2022-11-21 12:35:30")
        try:
            faktura_rad.user_id = get_user_id_for_fasit_user(fasit_rad.attribute_anvandare)
        except NoUserFoundError:
            return FakturaRadState.SPLIT_INCOMPLETE, "dela_enl_fasit_agare -> NoUserFoundError"
        faktura_rad.user_aktivitet_char = Aktivitet(s.query(Staff_dbo.aktivitet_char).filter(Staff_dbo.user_id == faktura_rad.user_id).first()[0])
        if faktura_rad.user_aktivitet_char is None or faktura_rad.user_aktivitet_char == Aktivitet.N:
            faktura_rad.split_status = FakturaRadState.SPLIT_INCOMPLETE
            faktura_rad.split_method_used = "dela_enl_fasit_agare -> user_aktivitet_char is None"
            return
        bibliotekarier = flatten_row(s.query(Staff_dbo.user_id).filter(Staff_dbo.titel.startswith("Biblio")).all())
        janitors = flatten_row(s.query(Staff_dbo.user_id).filter(Staff_dbo.titel.startswith("Vaktm")).all())
        if faktura_rad.user_id in bibliotekarier:  # ["tinasp", "magbro"]:  # bibliotekets kostnader går över hela skolan
            faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=faktura_rad.dela_over_enheter, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
            faktura_rad.split_method_used = "Kontering>Bibliotek"
            faktura_rad.split_status = FakturaRadState.SPLIT_BY_FASIT_USER_SUCCESSFUL
            insert_split_into_database(faktura_rad=faktura_rad)
            return
        elif faktura_rad.user_id in janitors:  # ["jonbjc", "kenchr"]:  # vaktmästarnas kostnader går över hela skolan

            faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=faktura_rad.dela_over_enheter, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
            faktura_rad.split_status = FakturaRadState.SPLIT_BY_FASIT_USER_SUCCESSFUL
            faktura_rad.split_method_used = "Kontering>Vaktmästare"
            insert_split_into_database(faktura_rad=faktura_rad)
            return
        elif faktura_rad.user_id == "lyadol":
            if fasit_rad.eunomia_kontering is None or "Personlig utr" not in fasit_rad.eunomia_kontering:
                faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=["656", "655"], month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
                faktura_rad.split_method_used = "Kontering>IT-Tekniker Buffert"
                faktura_rad.user_aktivitet_char = Aktivitet.P  # Min buffert ska gå som pedagogisk kostnad
                faktura_rad.split_status = FakturaRadState.SPLIT_BY_FASIT_USER_SUCCESSFUL
                insert_split_into_database(faktura_rad=faktura_rad)
                return
            else:
                faktura_rad.split = gen_tjf_for_staff(user_id=faktura_rad.user_id, month_nr=faktura_rad.faktura_month)
                faktura_rad.split_status = FakturaRadState.SPLIT_BY_FASIT_KONTERING_SUCCESSFUL
                faktura_rad.split_method_used = "Kontering>IT-Tekniker Personlig utr"
                insert_split_into_database(faktura_rad=faktura_rad)
                return
        else:
            faktura_rad.split_status = FakturaRadState.SPLIT_BY_FASIT_USER_SUCCESSFUL
            faktura_rad.split_method_used = "Delad enligt gen tjf"
            try:
                faktura_rad.split = gen_tjf_for_staff(user_id=faktura_rad.user_id, month_nr=faktura_rad.faktura_month)
            except NoTjfFoundError as e:
                if is_staff_old(faktura_rad.user_id):
                    faktura_rad.split_status = FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL
                    faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=faktura_rad.dela_over_enheter, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
                    faktura_rad.split_method_used = "Delad enligt elevantal"
                    insert_split_into_database(faktura_rad=faktura_rad)
                    return
                else:
                    raise NoTjfFoundError(f"Kunde inte hitta tjf för {faktura_rad.user_id} i {faktura_rad.faktura_month}") from e
            else:
                insert_split_into_database(faktura_rad=faktura_rad)
                return


def dela_enl_fasit_kontering(*, faktura_rad: FakturaRad_dbo, verbose: bool = False, manuell_kontering: str = None, notering: str = None) -> FakturaRadState:
    """ Dela enligt fasit kontering
    :param notering:        :type str: läggs längst bak i konteringen som information till sammanställningen
    :param verbose:         :type bool: vill du att stack information ska skrivas ut
    :param faktura_rad:     :type faktura_rad: faktura objektet som ska delas
    :type manuell_kontering :type str : med manuell kontering i formatet  "Kontering>Elevantal<656;655|aktivitet:p"
    """
    if verbose:
        print(f"Dela_enl_fasit_kontering start                         2022-11-21 12:55:46")
    s = MysqlDb().session()
    fasit_rad = s.query(FasitCopy).filter(FasitCopy.name == faktura_rad.avser).first()
    faktura_rad.split_method_used = False
    if fasit_rad is None or fasit_rad.eunomia_kontering is None or len(fasit_rad.eunomia_kontering) == 0:
        return FakturaRadState.SPLIT_INCOMPLETE, "Fail dela_enl_fasit_kontering fail no kontering in fasit"
    else:
        if verbose:
            print(f"{fasit_rad.eunomia_kontering:},                            2022-11-21 12:56:24")
        if manuell_kontering is None:
            decode_kontering_in_fritext(faktura_rad=faktura_rad, konterings_string=fasit_rad.eunomia_kontering)
        else:
            decode_kontering_in_fritext(faktura_rad=faktura_rad, konterings_string=F"Manuell kontering: |{manuell_kontering}")
        if faktura_rad.split_method_used is False:  # betyder att vi inte ska köra på fasit kontering för denna rad, trots att det finns konterings info
            faktura_rad.split_method_used = "Fail dela_enl_fasit_kontering fail no kontering in fasit"
            faktura_rad.split_status = FakturaRadState.SPLIT_INCOMPLETE
            return
        faktura_rad.split_method_used += notering
        success = insert_split_into_database(faktura_rad=faktura_rad)
        if success:
            faktura_rad.split_status = FakturaRadState.SPLIT_BY_FASIT_KONTERING_SUCCESSFUL
            return
        else:
            faktura_rad.split_method_used = "Fail dela_enl_fasit_kontering fail no kontering in fasit"
            faktura_rad.split_status = FakturaRadState.SPLIT_INCOMPLETE
            return


def split_row(months: list[str] = None, verbose: bool = False, avser: str = None, row_ids: list[int] = None) -> None:
    """ split row """
    s = MysqlDb().session()
    # if avser is None and row_ids is None:
    #     behandla_dela_cb()

    if avser is not None:
        rader = s.query(FakturaRad_dbo).filter(and_(or_(FakturaRad_dbo.split_done == None, FakturaRad_dbo.split_done == 0),
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
        # tillfälligt fel som funkar i framtiden då eunomia körs aktuellt.
        if faktura_rad.avser == "E47180":  # Nya Pykologens dator
            faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=EnhetsAggregering.GRU7_9, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
            faktura_rad.split_method_text = "Nya Psykologen enligt elevantal"
            insert_split_into_database(faktura_rad=faktura_rad)
            continue
        # if faktura_rad.anvandare in {"Wallin, Gunilla (walgun)"}:  # gamla antställdas grejer ADMIN
        #     faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=EnhetsAggregering.FOLKUNGA, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
        #     faktura_rad.user_aktivitet_char = Aktivitet.A
        #     faktura_rad.split_method_used = "Manuell hantering- Wallin"
        #     faktura_rad.split_status = FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL
        #     insert_split_into_database(faktura_rad=faktura_rad)
        #     continue
        # if faktura_rad.anvandare in {'Carbonnier, Charlotte (chacar)',
        #                              'Ståhlberg, Lars Henning (larsta)',
        #                              'Landelius, Ann-Charlotte (landan)',
        #                              'Sundstedt, Sanna (sansun)'}:  # gamla antställdas grejer FOLKUNGA PEDAGOGER
        #     faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=EnhetsAggregering.FOLKUNGA, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
        #     faktura_rad.user_aktivitet_char = Aktivitet.P
        #     faktura_rad.split_method_used = "Manuell hantering - gamla anställda"
        #     faktura_rad.split_status = FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL
        #     insert_split_into_database(faktura_rad=faktura_rad)
        #     continue

        if verbose:
            print("Dela enligt Fasit ägare                             2022-11-21 12:33:22")
        # faktura_rad.split_status = FakturaRadState.SPLIT_INCOMPLETE
        dela_enl_fasit_kontering(faktura_rad=faktura_rad)  # Första delnings prioriteten är att dela på fasit Kontering

        # förbered generell enhet att dela raden över
        set_school_information(faktura_rad=faktura_rad)

        # Fasta delningar beroende på tjänst
        if faktura_rad.avser == "Pgm Adobe CC for EDU K12":  # A513
            faktura_rad.split_method_text = F"Pgm Adobe CC"
            faktura_rad = dela_enl_fasit_kontering(faktura_rad, manuell_kontering="Kontering>Elevantal<656;655|aktivitet:p")
            insert_split_into_database(faktura_rad=faktura_rad)

        # Databas beroende delningar
        if faktura_rad.split_status == FakturaRadState.SPLIT_INCOMPLETE:
            faktura_rad.split_status = dela_enl_fasit_agare(faktura_rad)
        if faktura_rad.split_status == FakturaRadState.SPLIT_INCOMPLETE:
            fasit_rad = get_fasit_row(name=faktura_rad.avser)
            if fasit_rad is not None:
                if fasit_rad.dela_pa_elevantal():
                    faktura_rad.split_status = FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL
                    insert_split_into_database(faktura_rad=faktura_rad,
                                               split=calc_split_on_student_count(enheter_to_split_over=faktura_rad.dela_over_enheter,
                                                                                 month=faktura_rad.faktura_month,
                                                                                 year=faktura_rad.faktura_year),
                                               split_method="elevantal")
                elif fasit_rad.dela_pa_gen_tjf():
                    faktura_rad.split_status = FakturaRadState.SPLIT_BY_GENERELL_TFJ_SUCCESSFUL
                    insert_split_into_database(faktura_rad=faktura_rad,
                                               split=get_tjf_for_enhet(enheter=faktura_rad.dela_over_enheter,
                                                                       month=faktura_rad.faktura_month),
                                               split_method="Generell tjf")
                # if all else fails
        if faktura_rad.split_status == FakturaRadState.SPLIT_INCOMPLETE:
            insert_failsafe_row(faktura_rad)


if __name__ == "__main__":
    # gen_split_by_elevantal(enheter=["654300", "654400"])
    # generate_total_tjf_for_month(1)
    # behandla_dela_cb()

    # gear_id = "E47732"
    # reset_avser(gear_id)
    # split_row(months=["7", "8", "9", "10", "11", "12"], avser=gear_id)
    #
    row_id = [12393]
    reset_faktura_row_id(row_ids=row_id)
    split_row(row_ids=row_id, verbose=False)

    # split_row(months=["7", "8", "9", "10", "11", "12"])

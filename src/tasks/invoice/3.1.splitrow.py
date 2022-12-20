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
from utils.faktura_utils._3_666_Insert_invoice_to_database import insert_split_into_database
from utils.faktura_utils._3_1_kontering import decode_kontering_in_fritext
from utils.faktura_utils._3_0_print_table import print_headers, COL_WIDTHS, print_start
from utils.faktura_utils._3_0_reset_rows import reset_faktura_row_id
from utils.flatten import flatten_row





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

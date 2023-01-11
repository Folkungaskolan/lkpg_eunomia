""" Hanterar uppdelning av fakturarader """

from sqlalchemy import or_
from sqlalchemy.sql.elements import and_

from database.models import FakturaRad_dbo
from database.mysql_db import MysqlDb
from utils.EunomiaEnums import FakturaRadState
from utils.dbutil.fasit_db import get_fasit_row
from utils.faktura_utils._3_0_print_table import print_headers
from utils.faktura_utils._3_3_1_Split_by_user import dela_enl_fasit_agare
from utils.faktura_utils._3_3_1_set_school_info import set_school_information
from utils.faktura_utils._3_3_2_Split_by_fasit_database import dela_enl_fasit_kontering
from utils.faktura_utils._3_3_3_Split_by_group import dela_gen_tjf_totaler, dela_elevantal, insert_pgm_adobe
from utils.faktura_utils._3_666_Insert_invoice_to_database import insert_failsafe_row


def split_row(months: list[str] = None, verbose: bool = False, avser: str = None, row_ids: list[int] = None) -> None:
    """ split row """
    s = MysqlDb().session()
    # if avser is None and row_ids is None:
    #     behandla_dela_cb()

    if avser is not None:
        rader = s.query(FakturaRad_dbo).filter(and_(or_(FakturaRad_dbo.split_done == None, FakturaRad_dbo.split_done == 0),
                                                    FakturaRad_dbo.faktura_year == 2022, FakturaRad_dbo.faktura_month.in_(months),
                                                    FakturaRad_dbo.avser == avser)
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
    print_headers()
    for faktura_rad in rader:
        if faktura_rad.tjanst.startswith("Ärende"):  ## Hoppa över ärenden för nu
            continue
        # faktura_rad.split_status = FakturaRadState.SPLIT_INCOMPLETE
        dela_enl_fasit_kontering(faktura_rad=faktura_rad)  # Första delnings prioriteten är att dela på fasit Kontering

        # Fasta delningar beroende på tjänst
        if faktura_rad.avser == "Pgm Adobe CC for EDU K12":  # A513
            insert_pgm_adobe()
            continue

        # Databas beroende delningar
        if faktura_rad.split_status == FakturaRadState.SPLIT_INCOMPLETE:  # DELA PÅ FASIT ÄGARE
            # förbered generell enhet att dela raden över
            set_school_information(faktura_rad=faktura_rad)
            faktura_rad.split_status = dela_enl_fasit_agare(faktura_rad)
        if faktura_rad.split_status == FakturaRadState.SPLIT_INCOMPLETE:
            fasit_rad = get_fasit_row(name=faktura_rad.avser)
            if fasit_rad is not None:
                if fasit_rad.ska_vi_standard_dela_pa_elevantal():
                    dela_elevantal(faktura_rad)
                elif fasit_rad.ska_vi_standard_dela_pa_gen_tjf():
                    dela_gen_tjf_totaler(faktura_rad)
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
    # row_id = [13501]
    # reset_faktura_row_id(row_ids=row_id)
    # split_row(row_ids=row_id, verbose=False)
    #
    split_row(months=["12"])
    # "V2482" ska ej betalas längre

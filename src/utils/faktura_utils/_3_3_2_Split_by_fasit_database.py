""" split by FASIT database Kontering"""
from database.models import FasitCopy, FakturaRad_dbo
from database.mysql_db import MysqlDb
from utils.EunomiaEnums import FakturaRadState
from utils.faktura_utils._3_0_print_table import printfakturainfo
from utils.faktura_utils._3_1_kontering import decode_kontering_in_fritext
from utils.faktura_utils._3_666_Insert_invoice_to_database import insert_split_into_database

@printfakturainfo
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
    faktura_rad.split_method_used = ""
    if fasit_rad is None or fasit_rad.eunomia_kontering is None or len(fasit_rad.eunomia_kontering) == 0:
        faktura_rad.split_method_used = "Fail dela_enl_fasit_kontering fail no kontering in fasit"
        return
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
        if notering is not None:
            faktura_rad.split_method_used = F"{faktura_rad.split_method_used} {notering}"
        success = insert_split_into_database(faktura_rad=faktura_rad)
        if success:
            faktura_rad.split_status = FakturaRadState.SPLIT_BY_FASIT_KONTERING_SUCCESSFUL
            return
        else:
            faktura_rad.split_method_used = "Fail dela_enl_fasit_kontering fail no kontering in fasit"
            faktura_rad.split_status = FakturaRadState.SPLIT_INCOMPLETE
            return

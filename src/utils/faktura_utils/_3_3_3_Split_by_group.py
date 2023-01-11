""" Fakturadelning utifrån en grupp av personer """
from database.models import FakturaRad_dbo
from utils.EunomiaEnums import FakturaRadState, Aktivitet
from utils.dbutil.staff_db import get_tjf_for_enhet
from utils.dbutil.student_db import calc_split_on_student_count
from utils.faktura_utils._3_0_print_table import printfakturainfo
from utils.faktura_utils._3_3_2_Split_by_fasit_database import dela_enl_fasit_kontering
from utils.faktura_utils._3_666_Insert_invoice_to_database import insert_split_into_database


@printfakturainfo
def dela_gen_tjf_totaler(faktura_rad):
    """ Dela vad som än kommer in på generell tjf totaler """
    faktura_rad.split_status = FakturaRadState.SPLIT_BY_GENERELL_TFJ_SUCCESSFUL
    faktura_rad.split_method_used = "Generell tjf"
    faktura_rad.user_aktivitet_char = Aktivitet.P
    faktura_rad.split = get_tjf_for_enhet(enheter=faktura_rad.dela_over_enheter, month=faktura_rad.faktura_month)
    insert_split_into_database(faktura_rad=faktura_rad)

@printfakturainfo
def insert_pgm_adobe(faktura_rad:FakturaRad_dbo)->None:
    """ Kör Adobe uppdelningen direkt """
    faktura_rad.split_method_text = F"Pgm Adobe CC"
    faktura_rad.split_status = dela_enl_fasit_kontering(faktura_rad, manuell_kontering="Kontering>Elevantal<656;655|aktivitet:p")
    insert_split_into_database(faktura_rad=faktura_rad)

@printfakturainfo
def dela_elevantal(faktura_rad):
    """ Dela vad som än kommer in på elevantal"""
    faktura_rad.split_status = FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL
    faktura_rad.split_method_used = F"Delat på elevantal"
    faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=faktura_rad.dela_over_enheter, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
    insert_split_into_database(faktura_rad=faktura_rad)


if __name__ == '__main__':
    pass

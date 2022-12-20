""" Faktura delnings metoder för delning av faktura raden utifrån en persons tjf"""
from CustomErrors import NoTjfFoundError, NoUserFoundError
from database.models import Staff_dbo, FasitCopy, FakturaRad_dbo
from database.mysql_db import MysqlDb
from utils.EunomiaEnums import FakturaRadState, Aktivitet
from utils.dbutil.fasit_db import get_user_id_for_fasit_user
from utils.dbutil.staff_db import is_staff_old, gen_tjf_for_staff
from utils.dbutil.student_db import calc_split_on_student_count
from utils.faktura_utils._3_0_print_table import printfakturainfo
from utils.faktura_utils._3_666_Insert_invoice_to_database import insert_split_into_database

from utils.flatten import flatten_row

@printfakturainfo
def dela_enl_fasit_agare(faktura_rad: FakturaRad_dbo, verbose: bool = False) -> None:
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
            faktura_rad.split_method_used = "Delad enligt Persons tjf"
            try:
                faktura_rad.split = gen_tjf_for_staff(user_id=faktura_rad.user_id, month_nr=faktura_rad.faktura_month)
                insert_split_into_database(faktura_rad=faktura_rad)
                return
            except NoTjfFoundError as e:
                if is_staff_old(user_id=faktura_rad.user_id):
                    faktura_rad.split_status = FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL
                    faktura_rad.split_method_used = "Delad enligt elevantal"
                    faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=faktura_rad.dela_over_enheter, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
                    insert_split_into_database(faktura_rad=faktura_rad)
                    return
                else:
                    # raise NoTjfFoundError(f"Kunde inte hitta tjf för {faktura_rad.user_id} i månad {faktura_rad.faktura_month}") from e
                    faktura_rad.split_status = FakturaRadState.SPLIT_INCOMPLETE
                    faktura_rad.split_method_used = "dela_enl_fasit_agare -> NoTjfFoundError"
                    return


if __name__ == '__main__':
    pass

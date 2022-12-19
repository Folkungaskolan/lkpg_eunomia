""" konterings hjälp funktioner"""
import inspect

from CustomErrors import AktivitetNotFoundError
from database.models import StudentCount_dbo, FakturaRad_dbo
from database.mysql_db import MysqlDb
from utils.EunomiaEnums import FakturaRadState
from utils.dbutil.student_db import calc_split_on_student_count
from utils.faktura_utils.normalize import normalize
from utils.student.student import get_id_komplement_pa_for_student


def decode_kontering_in_fritext(*, faktura_rad: FakturaRad_dbo, konterings_string: str, verbose: bool = False) -> (dict[str:float], str, str):
    """ Decode fritextfield
    Returnerar {"123456": 0.5, "123457": 0.5}
    och "p" som instruktion för aktivitet
    och "konterings kommentar"
    Alternativ:
    Kontering>A513
    Kontering>GruTeknik
    Kontering>Musikproduktion
    Kontering>FolkungaBibliotek
    Kontering>DirektElev>användarnamn
    Kontering>Enheter<656:0.1;655:0.9     exv
    Kontering>Enheter<656:0.1;655:*      * innebär "resten"
    Kontering>DirektElev<användarnamn
    """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()
    code_segments = konterings_string.split("|")
    temp_kontering = {}
    star_present_in_key = None
    aktivitet = None
    for code_segment in code_segments:
        if code_segment.startswith("Kontering"):
            faktura_rad.split_method_used = code_segment
            remaining_code_segment = code_segment.split(">")[1]  # Enheter>656:0.1;655:0.9
            if remaining_code_segment == "A513":  # Delas över Gymnasiet
                return calc_split_on_student_count(enheter_to_split_over=["655"],  # Delas över Gymnasiet
                                                   month=faktura_rad.faktura_month,
                                                   year=faktura_rad.faktura_year), "p", "Kontering>A513"
            elif remaining_code_segment == "GruTeknik":  # Delas över grundskolans elever
                return calc_split_on_student_count(enheter_to_split_over=["656"],  # Delas över Grundskolans elever
                                                   month=faktura_rad.faktura_month,
                                                   year=faktura_rad.faktura_year), "p", "Kontering>GruTeknik"
            elif remaining_code_segment == "Musikproduktion":  # Delas över grundskolan
                return {"656520": 1}, "p", "Kontering>Musikproduktion"  # generate_split_on_student_count(enheter=["656520"],  # Delas över Grundskolans 7-9 elever
            elif remaining_code_segment == "FolkungaBibliotek":  # Delas över grundskolan
                return calc_split_on_student_count(enheter_to_split_over=["656", "655"],  # Delas över Gymnasiet och Grundskolan enligt antal elever
                                                   month=faktura_rad.faktura_month,
                                                   year=faktura_rad.faktura_year), "p", "Kontering>FolkungaBibliotek"
            elif remaining_code_segment.startswith("DirektElev"):  # Delas över den enheten som en elev tillhör
                elev_anvandarnamn = remaining_code_segment.split("<")[1]  # Kontering>DirektElev<användarnamn    'Kontering>DirektElev<malmos795'
                faktura_rad.anvandare = elev_anvandarnamn
                faktura_rad.user_id = elev_anvandarnamn
                return calc_split_on_student_count(enheter_to_split_over=get_id_komplement_pa_for_student(user_id=elev_anvandarnamn),  # Delas över Gymnasiet
                                                   month=faktura_rad.faktura_month,
                                                   year=faktura_rad.faktura_year), "p", code_segment
            elif remaining_code_segment.startswith("Enheter"):
                faktura_rad.split = gen_kontering_enheter(kontering=remaining_code_segment, verbose=verbose)
            elif remaining_code_segment.startswith("Elevantal"):
                faktura_rad.split = gen_kontering_elev_antal(kontering=remaining_code_segment, verbose=verbose)
            elif remaining_code_segment.startswith("Personlig utr"):  # mina personliga grejer ska konteras efter min Tjf
                faktura_rad.split_status = FakturaRadState.SPLIT_INCOMPLETE  # Skickar tillbaka falskt så raden misslyckas med konteringen och kör på Fasit ägaren
            else:
                raise NotImplementedError(f"Solution for kontering not implemented {konterings_string}")
        elif code_segment.startswith("aktivitet"):  # hämta aktivtet från sträng
            faktura_rad.aktivitet = code_segment.split(":")[1]
    if faktura_rad.aktivitet is None:
        raise AktivitetNotFoundError(f"ingen aktivitet hittad i konterings_string:{konterings_string}")
    return faktura_rad.split, faktura_rad.aktivitet, faktura_rad.split_method_used  # för test av kontering


def gen_kontering_enheter(kontering: str, verbose: bool = False) -> tuple[str, str, str]:
    """ Hanterar kontering om konterings metoden är 'enhet' """
    star_present_in_key = None  # init check variabale
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")
    kontering = kontering.split("<")[1]
    t_kontering = kontering.split(";")
    slut_kontering: dict[str:float] = {}
    for enhets_kontering in t_kontering:
        if verbose:
            print(enhets_kontering)
        key, value = enhets_kontering.split(":")
        if value == "*":
            star_present_in_key = key
            continue
        else:
            slut_kontering[key] = float(value.replace(",", "."))
    if star_present_in_key is not None:
        slut_kontering[star_present_in_key] = 1 - sum(slut_kontering.values())
    return slut_kontering


def gen_kontering_elev_antal(kontering: str, verbose: bool = False) -> tuple[str, str, str]:
    """ Hanterar konterings split om konterings metoden är 'Elevantal' """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()
    elev_enhet_str = kontering.split("<")[1]
    elev_enhet_lista = elev_enhet_str.split(";")
    student_counts = {}
    for k in elev_enhet_lista:
        if verbose:
            print(k)
        counts = s.query(StudentCount_dbo).filter(StudentCount_dbo.id_komplement_pa.startswith(k)).all()
        for c in counts:
            student_counts[c.id_komplement_pa] = c.count
    slut_kontering = normalize(student_counts)  # se till att det summerar till 1
    return slut_kontering


if __name__ == '__main__':
    # print(decode_kontering_in_fritext(
    #     "Tidigare kommentar|Kontering>Enheter<655119:1;655123:2;655122:3;655125:4;656510:5;656520:6;656310:7;654100:8;654200:9;654300:10;654400:11|aktivitet:p"))
    print(decode_kontering_in_fritext(konterings_string="Kontering>Elevantal<656;655|aktivitet:p",
                                      faktura_rad=FakturaRad_dbo(faktura_month=10, faktura_year=2022)
                                      )
          )
    print(decode_kontering_in_fritext(konterings_string="Tidigare kommentar|Kontering>Elevantal<655119;655122|aktivitet:p",
                                      faktura_rad=FakturaRad_dbo(faktura_month=10, faktura_year=2022)
                                      )
          )
    print(decode_kontering_in_fritext(konterings_string="Tidigare kommentar|Kontering>Elevantal<655119;655122|aktivitet:p",
                                      faktura_rad=FakturaRad_dbo(faktura_month=10, faktura_year=2022)
                                      )
          )

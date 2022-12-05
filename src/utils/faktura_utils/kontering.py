""" konterings hjälp funktioner"""
import inspect

from CustomErrors import AktivitetNotFoundError
from database.models import StudentCount_dbo
from database.mysql_db import MysqlDb
from utils.dbutil.student_db import generate_split_on_student_count
from utils.faktura_utils.normalize import normalize


def decode_kontering_in_fritext(*, faktura_month: int, faktura_year: int, konterings_string: str, verbose: bool = False) -> (dict[str:float], str, str):
    """ Decode fritextfield
    Returnerar {"123456": 0.5, "123457": 0.5}
    och "p" som instruktion för aktivitet
    och "konterings kommentar"

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
            metod_string = code_segment
            if code_segment == "Kontering>A513":  # Delas över Gymnasiet
                return generate_split_on_student_count(enheter_to_split_over=["655"],  # Delas över Gymnasiet
                                                       month=faktura_month,
                                                       year=faktura_year), "p", "Kontering>A513"
            if code_segment == "Kontering>GruTeknik":  # Delas över grundskolans elever
                return generate_split_on_student_count(enheter_to_split_over=["656"],  # Delas över Grundskolans elever
                                                       month=faktura_month,
                                                       year=faktura_year), "p", "Kontering>GruTeknik"
            if code_segment == "Kontering>Musikproduktion":  # Delas över grundskolan
                return {"656520": 1}, "p", "Kontering>Musikproduktion"  # generate_split_on_student_count(enheter=["656520"],  # Delas över Grundskolans 7-9 elever
                # month=faktura_rad.faktura_month,
                # year=faktura_rad.faktura_year), "p", "Kontering>Musikproduktion"
            if code_segment == "Kontering>FolkungaBibliotek":  # Delas över grundskolan
                return generate_split_on_student_count(enheter_to_split_over=["656", "655"],  # Delas över Gymnasiet och Grundskolan enligt antal elever
                                                       month=faktura_month,
                                                       year=faktura_year), "p", "Kontering>FolkungaBibliotek"

            faktura_rad = code_segment.split(">")[1]
            kontering_metod = faktura_rad.split("<")[0]
            if kontering_metod == "Enheter":
                faktura_rad = faktura_rad.split(";")
                for k in faktura_rad:
                    if verbose:
                        print(k)
                    key, value = k.split(":")
                    if value == "*":
                        star_present_in_key = key
                        continue
                    else:
                        temp_kontering[key] = float(value.replace(",", "."))
                if star_present_in_key is not None:
                    slut_kontering = temp_kontering
                    slut_kontering[star_present_in_key] = 1 - sum(temp_kontering.values())
                else:
                    slut_kontering = temp_kontering
            elif kontering_metod == "Elevantal":
                elev_enhet_str = faktura_rad.split("<")[1]
                elev_enhet_lista = elev_enhet_str.split(";")
                student_counts = {}
                for k in elev_enhet_lista:
                    if verbose:
                        print(k)
                    counts = s.query(StudentCount_dbo).filter(StudentCount_dbo.id_komplement_pa.startswith(k)).all()
                    for c in counts:
                        student_counts[c.id_komplement_pa] = c.count
                slut_kontering = normalize(student_counts)  # se till att det summerar till 1
            elif kontering_metod == "Personlig utr":  # mina personliga grejer ska konteras efter min Tjf
                return {"": 0.0}, False, False  # Skickar tillbaka falskt så raden misslyckas med konteringen och kör på Fasit ägaren

        elif code_segment.startswith("aktivitet"):  # hämta aktivtet från sträng
            aktivitet = code_segment.split(":")[1]
    if aktivitet is None:
        raise AktivitetNotFoundError(
            f"ingen aktivitet hittad i sträng {faktura_rad.id=}, {faktura_rad.avser=}, {faktura_rad.faktura_year=}, {faktura_rad.faktura_month=}")
    # print(sum(slut_kontering.values()))
    return slut_kontering, aktivitet, metod_string


if __name__ == '__main__':
    # print(decode_kontering_in_fritext(
    #     "Tidigare kommentar|Kontering>Enheter<655119:1;655123:2;655122:3;655125:4;656510:5;656520:6;656310:7;654100:8;654200:9;654300:10;654400:11|aktivitet:p"))
    print(decode_kontering_in_fritext(konterings_string="Kontering>Elevantal<656;655|aktivitet:p", faktura_month=10, faktura_year=2022))
    print(decode_kontering_in_fritext(konterings_string="Tidigare kommentar|Kontering>Elevantal<655119;655122|aktivitet:p", faktura_month=10, faktura_year=2022))

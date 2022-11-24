""" konterings hjälp funktioner"""
import json

from CustomErrors import AktivitetNotFoundError
from database.models import StudentCount_dbo
from database.mysql_db import MysqlDb
from utils.faktura_utils.normalize import normalize


def decode_kontering_in_fritext(kontering: str) -> (dict[str:float], str):
    """ Decode fritextfield """
    s = MysqlDb().session()
    code_segment = kontering.split("|")
    temp_kontering = {}
    star_present_in_key = None
    for seg in code_segment:
        if seg.startswith("Kontering"):
            kontering = seg.split(">")[1]
            kontering_metod = kontering.split("<")[0]
            if kontering_metod == "Enheter":
                kontering = kontering.split(";")
                for k in kontering:
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
                kontering = kontering.split("<")[1]
                kontering = kontering.split(";")
                student_counts = {}
                for k in kontering:
                    print(k)
                    counts = s.query(StudentCount_dbo).filter(StudentCount_dbo.id_komplement_pa.startswith(k)).all()
                    for c in counts:
                        student_counts[c.id_komplement_pa] = c.count
                slut_kontering = normalize(student_counts)  # se till att det summerar till 1

        elif seg.startswith("aktivitet"):  # hämta aktivtet från sträng
            aktivitet = seg.split(":")[1]
    if aktivitet is None:
        raise AktivitetNotFoundError(f"ingen aktivitet hittad i sträng")
    # print(sum(slut_kontering.values()))
    return slut_kontering, aktivitet


if __name__ == '__main__':
    # print(decode_kontering_in_fritext(
    #     "Tidigare kommentar|Kontering>Enheter<655119:1;655123:2;655122:3;655125:4;656510:5;656520:6;656310:7;654100:8;654200:9;654300:10;654400:11|aktivitet:p"))
    print(decode_kontering_in_fritext("Kontering>Elevantal<656;655|aktivitet:p"))
    print(decode_kontering_in_fritext("Tidigare kommentar|Kontering>Elevantal<655119;655122|aktivitet:p"))

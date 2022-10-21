""" Utveckling av tjänstefördelningarna """
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy.sql.elements import and_

from database.models import Tjf_dbo, Staff_dbo
from database.mysql_db import init_db
from settings.folders import FAKTURA_EXCEL_TJF_FOLDER
from utils.decorators import function_timer
from utils.pnr_utils import pnr10_to_pnr12


def find_enhets_tjf_file(enhet: str) -> Path:
    """ Hittar tjf filen för en enhet """
    filelist = list(Path(FAKTURA_EXCEL_TJF_FOLDER).rglob('*.[Xx][Ll][Ss][Mm]'))
    for filepath in filelist:
        if enhet in str(filepath.stem):
            return filepath


def import_tjf_alla_enheter(enheter: list = ["654", "655", "656"]) -> None:
    """ Importerar tjänstefördelningarna för alla enheter """
    for enhet in enheter:
        import_tjf_for_enhet(enhet)
    pass


@function_timer
def import_tjf_for_enhet(enhet: str) -> None:
    """ Importerar tjänstefördelningarna för en enhet från tjf filen """
    tjf_filepath = find_enhets_tjf_file(enhet)
    print(tjf_filepath)
    df = pd.read_excel(tjf_filepath, skiprows=1, usecols="A:S", sheet_name="Hämtningsflik LINQ", dtype=str)
    df = df.dropna(subset=["Personnr"])
    df = df.replace(np.nan, "")
    df = df[df["Personnr"] != "7501010101"]
    session = init_db()
    for index, row in df.iterrows():
        # print(row)
        staff = session.query(Staff_dbo).filter(Staff_dbo.pnr12 == pnr10_to_pnr12(row["Personnr"])).first()
        if staff is None:  # om vi inte har en användare så skapas en.
            staff = Staff_dbo(pnr12=pnr10_to_pnr12(row["Personnr"]))
            staff.full_name = row["Namn"]
            staff.domain = "update_from_web"
            staff.titel = row["Yrke"]
        tjf = session.query(Tjf_dbo).filter(and_(Tjf_dbo.id_komplement_pa == row["ID/Komplement/PA"],
                                                 Tjf_dbo.pnr12 == pnr10_to_pnr12(row["Personnr"]))).first()
        if tjf is None:
            tjf = Tjf_dbo(pnr12=pnr10_to_pnr12(row["Personnr"]),
                          id_komplement_pa=row["ID/Komplement/PA"])
        tjf.id_komplement_pa = row["ID/Komplement/PA"]
        tjf.year = "2022"
        tjf.jan = row["Jan"]
        tjf.feb = row["Feb"]
        tjf.mar = row["Mar"]
        tjf.apr = row["Apr"]
        tjf.maj = row["Maj"]
        tjf.jun = row["Jun"]
        tjf.jul = row["Jul"]
        tjf.aug = row["Aug"]
        tjf.sep = row["Sep"]
        tjf.okt = row["Okt"]
        tjf.nov = row["Nov"]
        tjf.dec = row["Dec"]
        tjf.kommentar = row["Kommentar"]
        tjf.yrke = row["Yrke"]
        tjf.personalkategori = row["Personalkategori"]
        session.add(staff)
        session.add(tjf)
    session.commit()


def fill_numeric_aktivitet() -> None:
    """ Fyller i aktivitet med korrekt numerisk aktivivitet om det är tomt """
    aktivitet_str_to_int: dict = {}
    pass


@cache
def determine_aktivitet_from_id(id_pa: str, aktivitet_char: str) -> str:
    """ Avgör aktivitet baserat på id_pa och aktivitet_s """
    GRU = ["656510", "656520", "656310"]
    GY = ["655119", "655123", "655122", "655125", "654100", "654200", "654300", "654400"]
    #     EK      , ES      , SA      , stlars ESmus,ESbild, NA     , IMA
    if id_pa in GY and aktivitet_char == "p":  # GY p
        return "410200"
    if id_pa in GY and aktivitet_char == "e":  # GY e
        return "410600"
    if id_pa in GY and aktivitet_char == "a":  # GY a
        return "410800"

    if id_pa in GRU and aktivitet_char == "p":  # GRU p
        return "310200"
    if id_pa in GRU and aktivitet_char == "e":  # GRU e
        return "310600"
    if id_pa in GRU and aktivitet_char == "a":  # GRU a
        return "310800"


def generate_aktivitet_from_tjf() -> None:  # Done
    """ Genererar aktivitet baserat på tjf """
    local_session = init_db()
    tjf_list = local_session.query(Tjf_dbo.id, Tjf_dbo.id_komplement_pa, Staff_dbo.aktivitet_char).join(Staff_dbo, Tjf_dbo.pnr12 == Staff_dbo.pnr12) \
        .filter(Tjf_dbo.aktivitet == None).all()
    for row_id, id_komplement_pa, aktivitet_char in tjf_list:
        numeric_aktivitet = determine_aktivitet_from_id(id_pa=id_komplement_pa, aktivitet_char=aktivitet_char)
        local_session.query(Tjf_dbo).filter(Tjf_dbo.id == row_id).update({"aktivitet": numeric_aktivitet})
        print(f"tjf: id: {row_id}, id_komplement_pa: {id_komplement_pa}, aktivitet_char: {aktivitet_char}, numeric_aktivitet: {numeric_aktivitet}")
    local_session.commit()


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)
    import_tjf_alla_enheter()  # importerar tjänstefördelningarna för alla enheter
    generate_aktivitet_from_tjf()  # kontrollerar aktiviteter för personalens idn så de är redo för rad delningar

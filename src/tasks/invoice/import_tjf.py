""" Utveckling av tjänstefördelningarna """
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy.sql.elements import and_

from db.models import Tjf_dbo, Staff_dbo
from db.mysql_db import init_db
from settings.folders import FAKTURA_EXCEL_TJF_FOLDER
from utils.decorators import function_timer
from utils.file_utils.staff_db import calculate_missing_staff_pnr10


def find_enhets_tjf_file(enhet: str) -> str:
    """ Hittar tjf filen för en enhet """
    filelist = list(Path(FAKTURA_EXCEL_TJF_FOLDER).rglob('*.[Xx][Ll][Ss][Mm]'))
    for filepath in filelist:
        if enhet in str(filepath.stem):
            return filepath


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
        tjf = session.query(Tjf_dbo).filter(and_(Tjf_dbo.id_komplement_pa == row["ID/Komplement/PA"],
                                                 Tjf_dbo.pnr == row["Personnr"])).first()
        if tjf is None:
            tjf = Tjf_dbo(pnr=row["Personnr"], id_komplement_pa=row["ID/Komplement/PA"])
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
        session.add(tjf)
    session.commit()


def import_tjf_alla_enheter(enheter: list = ["654", "655", "656"]) -> None:
    """ Importerar tjänstefördelningarna för alla enheter """
    for enhet in enheter:
        import_tjf_for_enhet(enhet)
    pass


def match_tjf_pnr_to_staff():
    """ Matchar tjf pnr till staff pnr """
    local_session = init_db()

    # Kör för att uppdatera staff pnr10 om det saknas
    local_session = calculate_missing_staff_pnr10(session=local_session)

    tjf_rows_without_user_id = local_session.query(Tjf_dbo).filter(Tjf_dbo.user_id == None).all()
    for row in tjf_rows_without_user_id:
        print(row.pnr10)
        staff_reference = local_session.query(Staff_dbo).filter(Staff_dbo.pnr10 == row.pnr10).first()
        row.user_id = staff_reference.user_id
        local_session.commit()


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)
    # import_tjf_alla_enheter()
    match_tjf_pnr_to_staff()

""" Utveckling av tjänstefördelningarna """
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy.sql.elements import and_

from db.models import tjf_dbo, Staff_dbo
from db.mysql_db import init_db
from settings.folders import FAKTURA_EXCEL_TJF_FOLDER
from utils.decorators import function_timer


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
        tjf = session.query(tjf_dbo).filter(and_(tjf_dbo.id_komplement_pa == row["ID/Komplement/PA"],
                                                 tjf_dbo.pnr == row["Personnr"])).first()
        if tjf is None:
            tjf = tjf_dbo(pnr=row["Personnr"], id_komplement_pa=row["ID/Komplement/PA"])
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
    session = init_db()
    tjf_rows_without_user_id = session.query(tjf_dbo).filter(tjf_dbo.user_id == None).all()
    for row in tjf_rows_without_user_id:
        print(row.pnr)
        pass


def calculate_staff_pnr10() -> None:  # TODO move to Staff
    """ Beräknar staff pnr10 """
    session = init_db()
    staff_without_pnr10 = session.query(Staff_dbo).filter(Staff_dbo.pnr10 == None).all()
    for s in staff_without_pnr10:
        print(s)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)
    # import_tjf_alla_enheter()
    calculate_staff_pnr10()
    # match_tjf_pnr_to_staff()

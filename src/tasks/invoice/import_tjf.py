""" Utveckling av tjänstefördelningarna """
from pathlib import Path

import pandas as pd

from settings.folders import FAKTURA_EXCEL_TJF_FOLDER


def find_enhets_tjf_file(enhet: str) -> str:
    """ Hittar tjf filen för en enhet """
    filelist = list(Path(FAKTURA_EXCEL_TJF_FOLDER).rglob('*.[Xx][Ll][Ss][Mm]'))
    for filepath in filelist:
        if enhet in str(filepath.stem):
            return filepath


def import_tjf_for_enhet(enhet: str) -> None:
    """ Importerar tjänstefördelningarna för en enhet från tjf filen """
    tjf_filepath = find_enhets_tjf_file(enhet)
    print(tjf_filepath)
    df = pd.read_excel(tjf_filepath, skiprows=1, usecols="A:S", sheet_name="Hämtningsflik LINQ")
    print(df)

if __name__ == '__main__':
    import_tjf_for_enhet("654")

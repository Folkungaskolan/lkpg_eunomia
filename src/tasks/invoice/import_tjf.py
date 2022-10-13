""" Utveckling av tjänstefördelningarna """
from pathlib import Path

from settings.folders import FAKTURA_EXCEL_TJF_FOLDER


def find_enhets_tjf_file(enhet: str) -> str:
    """ Hittar tjf filen för en enhet """
    filelist = list(Path(FAKTURA_EXCEL_TJF_FOLDER).rglob('*.[Xx][Ll][Ss][Mm]'))
    for filepath in filelist:
        if enhet in str(filepath.stem):
            return filepath


def import_tjf_for_enhet(enhet: str) -> None:
    """ Importerar tjänstefördelningarna för en enhet från tjf filen """


if __name__ == '__main__':
    print(find_enhets_tjf_file("656"))

""" funktioner för att hantera FASIT information"""

import pandas as pd

from settings.folders import FASIT_CSV_FILEPATH


def load_fasit_csv() -> pd.DataFrame:
    """ Ladda in csv filen med fasit informationen från disk"""
    df = pd.read_csv(FASIT_CSV_FILEPATH, encoding="latin-1", sep="\t", skiprows=1)
    # print(df.columns)
    # print(df)
    return df


def download_new_fasit_csv() -> None:
    """ Ladda ner en ny fasit csv fil från fasit"""
    pass
    # TODO: implementera nedladdning av fasit csv filen


def get_fasit_staff_users() -> pd.DataFrame:
    """ Hämta alla användare från fasit"""
    df = load_fasit_csv()
    staff_df = df[["name",
                   "attribute.användarnamn",
                   "attribute.epost",
                   "attribute.faktura",
                   "attribute.jobbtitel",
                   "attribute.kund",
                   "attribute.kundnummer",
                   "tag.användare"
                   ]]
    # print(staff_df)
    staff_df = staff_df[staff_df["tag.användare"] == 1]
    print(staff_df)
    return staff_df


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)
    get_fasit_staff_users()

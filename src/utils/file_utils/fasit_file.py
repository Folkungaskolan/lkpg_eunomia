""" funktioner för att hantera FASIT information"""
import pandas as pd
from settings.folders import FASIT_CSV_FILEPATH


def load_fasit_csv() -> pd.DataFrame:
    """ Ladda in csv filen med fasit informationen från disk"""
    df = pd.read_csv(FASIT_CSV_FILEPATH, encoding="latin-1", sep="\t", skiprows=1, dtype=str)
    return df


def download_new_fasit_csv() -> None:
    """ Ladda ner en ny fasit csv fil från fasit"""
    pass
    # TODO: implementera nedladdning av fasit csv filen


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)
    # load_fasit_to_db()
    # update_student_examen_year()

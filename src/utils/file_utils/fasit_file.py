""" funktioner för att hantera FASIT information"""
import pandas as pd
from settings.folders import FASIT_CSV_FILEPATH
from utils.path_utils import split_folder_path_from_filepath
from utils.web_utils.general_web import init_chrome_webdriver


def load_fasit_csv() -> pd.DataFrame:
    """ Ladda in csv filen med fasit informationen från disk"""
    df = pd.read_csv(FASIT_CSV_FILEPATH, encoding="latin-1", sep="\t", skiprows=1, dtype=str)
    return df


def download_new_fasit_csv(headless_bool:bool = True) -> None:
    """ Ladda ner FASIT som csv fil """
    # TODO: implementera nedladdning av fasit csv filen
    driver = init_chrome_webdriver(headless_bool=headless_bool,file_download_redirect_to_folder=split_folder_path_from_filepath(FASIT_CSV_FILEPATH))
    driver.get(url="https://onify.linkoping.se/workspace/fasit/export?term=*&export=csv")
    # driver.get(url="https://get.videolan.org/vlc/3.0.18/win32/vlc-3.0.18-win32.exe")


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)
    download_new_fasit_csv(headless_bool=False)
    # load_fasit_to_db()
    # update_student_examen_year()

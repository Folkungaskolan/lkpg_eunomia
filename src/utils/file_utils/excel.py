"""
Funktioner för att hantera skrivning av excel filer
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from pandas import DataFrame

from database.models import Student_dbo
from database.mysql_db import init_db
from settings.folders import STUDENT_USER_FOLDER_PATH, STUDENT_USER_XLSX_FILEPATH, STAFF_USER_XLSX_FILEPATH, \
    STAFF_USER_FOLDER_PATH, KLASSLISTA_CSV_FILEPATH, STUDENT_PW_CSV_FILEPATH
from utils.file_utils.json_wrapper import load_dict_from_json_path
from utils.print_progress_bar import print_progress_bar


def write_student_csv_from_mysql(verbose: bool = False) -> DataFrame:
    """
    Skriver om Json filer för eleverna till en csv och excel fil
    :param verbose: bool om det ska skrivas ut mer info i consolen
    :return: None
    """
    if verbose:
        print("write_student_csv_from_mysql start")

    local_session = init_db()
    student_df = pd.read_sql(local_session.query(Student_dbo.user_id,
                                                 Student_dbo.first_name,
                                                 Student_dbo.last_name,
                                                 Student_dbo.eduroam_pw,
                                                 Student_dbo.google_pw,
                                                 Student_dbo.klass).statement, local_session.bind)
    # används i nyckelhanteringen för att uppdatera klasslistorna på vilka elever som finns på skolan.
    student_df.to_csv(KLASSLISTA_CSV_FILEPATH, sep=';', encoding='utf-8', index=False)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)
    write_student_csv_from_mysql()


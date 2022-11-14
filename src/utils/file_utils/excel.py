"""
Funktioner för att hantera skrivning av excel filer
"""
import pandas as pd
from pandas import DataFrame

from database.models import Student_dbo
from database.mysql_db import MysqlDb
from settings.folders import KLASSLISTA_CSV_FILEPATH, STUDENT_PW_CSV_FILEPATH


def write_student_csv_from_mysql(verbose: bool = False) -> DataFrame:
    """
    Skriver om Json filer för eleverna till en csv och excel fil
    :param verbose: bool om det ska skrivas ut mer info i consolen
    :return: None
    """
    if verbose:
        print("write_student_csv_from_mysql start")

    s = MysqlDb().session()
    student_df = pd.read_sql(s.query(Student_dbo.user_id,
                                                 Student_dbo.first_name,
                                                 Student_dbo.last_name,
                                                 Student_dbo.klass).statement, s.bind)
    # används i nyckelhanteringen för att uppdatera klasslistorna på vilka elever som finns på skolan.
    student_df.to_csv(KLASSLISTA_CSV_FILEPATH, sep=';', encoding='utf-8', index=False)

    student_df = pd.read_sql(s.query(Student_dbo.user_id,
                                                 Student_dbo.first_name,
                                                 Student_dbo.last_name,
                                                 Student_dbo.eduroam_pw,
                                                 Student_dbo.google_pw,
                                                 Student_dbo.klass).statement, s.bind)
    # används i lösenords inmatningen för konfiguration av chromebooks
    student_df.to_csv(STUDENT_PW_CSV_FILEPATH, sep=';', encoding='utf-8', index=False)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)
    write_student_csv_from_mysql()

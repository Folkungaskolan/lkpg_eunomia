""" Funktioner som jobbar mot lärarna ämnen tabellen """
from io import StringIO

import pandas as pd
import pyperclip as pc
from sqlalchemy import and_

from database.models import StaffSubjects_dbo
from database.mysql_db import MysqlDb
from settings.folders import STAFF_USER_SUBJECTS_CSV
from utils.dbutil.staff_db import get_staff_user_from_db_based_on_user_id
from utils.flatten import flatten_row
from utils.print_progress_bar import print_progress_bar


def get_mentor_for_klass(klass_name: str) -> list[str]:
    """ Hämta mentorer för klassen returnerar mentoernas användarnamn """
    s = MysqlDb().session()
    mentors = s.query(StaffSubjects_dbo.user_id).filter(and_(StaffSubjects_dbo.subject == "MENTOR",
                                                             StaffSubjects_dbo.klass_grupp == klass_name
                                                             )
                                                        ).all()
    return flatten_row(mentors)

def read_skola24_information_from_windows_clipboard_to_df() -> pd.DataFrame:
    """ Read windows clipboard with skola to pandas dataframe """
    return pd.read_csv(StringIO(pc.paste()), sep="\t", dtype=str)  # läser clipboard till df, konverterar sträng till io för att härma fil för read_csv

def import_staff_subjects_from(*, read_clipboard: bool = True) -> None:
    """ Importera lärare ämnen från Windows klippboard annars från csv fil """
    reset_staff_subjects()
    s = MysqlDb().session()

    if read_clipboard:
        # https://sparkbyexamples.com/pandas/how-to-read-csv-from-string-in-pandas/
        df = read_skola24_information_from_windows_clipboard_to_df()
    else:
        df = pd.read_csv(STAFF_USER_SUBJECTS_CSV, encoding="utf-8", sep=",", dtype=str)
    # columns = df.columns
    # print(df.columns)
    df.fillna("", inplace=True)
    # print(df)

    prefix = 'Import subjects Progress:'
    print_progress_bar(0, len(df), prefix=prefix, suffix='Complete', length=50)

    for index, row in df.iterrows():
        # print(index)
        print_progress_bar(index, len(df), prefix=prefix, suffix='Complete', length=50)
        if (type(row["Lärare"]) is not str) or row["Lärare"] is None or len(row["Lärare"]) == 0:
            continue

        kategori = row["Kategori"]
        for sub in row["Ämne"].split(":"):
            if sub == "MT":
                sub = "MENTOR"
            elif "." in sub:
                sub = sub.replace(".", "")
            elif sub in set("M2SPA", "M2FRA","M2DEU"):
                sub = "Moderna Språk"

            for anv in row["Lärare"].split(","):
                if row["*Ingående klasser"] is None or (type(row["*Ingående klasser"]) is not str):
                    update_staff_subject_record(user_id=anv, subject=sub, kategori=kategori, klass_grupp="")
                else:
                    for klass in row["*Ingående klasser"].split(","):
                        update_staff_subject_record(user_id=anv, subject=sub, kategori=kategori, klass_grupp=klass)
    s.commit()
    print_progress_bar(len(df), len(df), prefix=prefix, suffix='Complete', length=50)


def update_staff_subject_record(*, user_id: str, kategori: str, klass_grupp: str, subject: str) -> None:
    """ Uppdaterar"""
    s = MysqlDb().session()
    if any(args is None for args in [user_id, kategori, klass_grupp, subject]) and any(args is None for args in [user_id, kategori, klass_grupp, subject]):
        raise ValueError("Alla argument måste vara satta")
    staff_subj_row = s.query(StaffSubjects_dbo).filter(and_(StaffSubjects_dbo.user_id == user_id,
                                                            StaffSubjects_dbo.kategori == kategori,
                                                            StaffSubjects_dbo.subject == subject,
                                                            StaffSubjects_dbo.klass_grupp == klass_grupp
                                                            )
                                                       ).all()
    if staff_subj_row is None or len(staff_subj_row) == 0:
        staffer = get_staff_user_from_db_based_on_user_id(user_id=user_id, create_on_missing=True)
        if staffer is None:
            raise ValueError(f"Kan inte hitta lärare med användarnamn: {user_id}")
        staff_subj_row = StaffSubjects_dbo(user_id=user_id,
                                           kategori=kategori,
                                           klass_grupp=klass_grupp,
                                           subject=subject,
                                           first_name=staffer.first_name,
                                           last_name=staffer.last_name,
                                           email=staffer.email,
                                           )
        s.add(staff_subj_row)


def reset_staff_subjects() -> None:
    """ Reset all staff mentors """
    s = MysqlDb().session()
    staff_subjects = s.query(StaffSubjects_dbo).all()
    for staff_subject in staff_subjects:
        s.delete(staff_subject)
    s.commit()


def transfer_user_info() -> None:
    """ Transfer user info from staff to staff_subjects """
    s = MysqlDb().session()
    staff_subjects = s.query(StaffSubjects_dbo).all()
    for staff_subject in staff_subjects:
        staff_subject.user_id = staff_subject.staff.user_id
    s.commit()

def run_full_staff_subject_import(read_clipboard=False) -> None:
    """ Run full staff subject import
    if read_clipboard is false it will read from csv file @ settings/folders.py STAFF_USER_SUBJECTS_CSV
    """
    reset_staff_subjects()
    import_staff_subjects_from(read_clipboard=read_clipboard)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 75)
    pd.set_option('display.expand_frame_repr', False)
    run_full_staff_subject_import(read_clipboard=False)


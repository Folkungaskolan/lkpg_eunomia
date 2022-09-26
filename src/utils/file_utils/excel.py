"""
Funktioner för att hantera skrivning av excel filer
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from settings.folders import STUDENT_USER_FOLDER_PATH, STUDENT_USER_XLSX_FILEPATH, STAFF_USER_XLSX_FILEPATH, STAFF_USER_FOLDER_PATH, KLASSLISTA_CSV_FILEPATH, STUDENT_PW_CSV_FILEPATH
from utils import print_progress_bar
from utils.file_utils import load_dict_from_json_path


def write_student_xlsx_from_json(verbose: bool = False):
    """
    Skriver om Json filer för eleverna till en csv och excel fil
    :param verbose:
    :return:
    """
    if verbose:
        print("write_student_xlsx_from_json start")

    filelist = list(Path(STUDENT_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))

    df_list = []
    filelist_len = len(filelist)
    print_progress_bar(0, filelist_len, prefix='Elever Export Progress:', suffix='Complete', length=150)
    for i, filepath in enumerate(filelist):
        print_progress_bar(iteration=i + 1, total=filelist_len, prefix=F'Elever Export Progress:{i}/{filelist_len}', suffix='Complete', length=150)

        try:
            user = load_dict_from_json_path(filepath=str(filepath))
        except json.decoder.JSONDecodeError:
            print(f" error on filepath : {filepath}                         2022-09-07 15:04:48")
            raise json.decoder.JSONDecodeError(msg=filepath)
        except Exception as e:
            print(f" error on filepath : {filepath}                         2022-09-07 15:04:51")
            raise Exception(e)
        else:
            df = pd.DataFrame(user, index=range(1, len(user.keys())))
            if verbose:
                print(df)
            df_list.append(df[:1])
    try:
        dfz = pd.concat(df_list, ignore_index=True, sort=False)
    except ValueError as e:
        raise ValueError(e)
    else:
        if verbose:
            print(dfz)
        dfz = dfz.replace(np.nan, "x", regex=True)
        dfz.to_csv(STUDENT_USER_FOLDER_PATH + 'elever.csv', sep=';', encoding='utf-8', index=False)
        if verbose:
            print(f"dfz {STUDENT_USER_FOLDER_PATH + 'elever.csv'} complete")

        # används som underlag för etiketter som jag skriver ut
        dfz.to_excel(STUDENT_USER_XLSX_FILEPATH, sheet_name='data', index=False)
        if verbose:
            print(f"dfz {STUDENT_USER_XLSX_FILEPATH} complete")

        # används i nyckelhanteringen för att uppdatera klasslistorna på vilka elever som finns på skolan.
        nyckel_hanterings_df = dfz[["account_1_user_name", "account_2_first_name", "account_2_last_name", "klass"]]
        nyckel_hanterings_df.to_csv(KLASSLISTA_CSV_FILEPATH, sep=';', encoding='utf-8', index=False)
        if verbose:
            print(f"dfz {KLASSLISTA_CSV_FILEPATH} complete")

        # används i hanteringen för generering av QR koder för att uppdatera klasslistorna på vilka elever som finns på skolan.
        nyckel_hanterings_df = dfz[["account_1_user_name", "account_2_first_name", "account_2_last_name", "account_3_eduroam_pw", "account_3_google_pw", "klass"]]
        nyckel_hanterings_df.to_csv(STUDENT_PW_CSV_FILEPATH, sep=';', encoding='utf-8', index=False)
        if verbose:
            print(f"dfz {KLASSLISTA_CSV_FILEPATH} complete")
        return dfz


def write_staff_xlsx_from_json(verbose: bool = False) -> None:
    """
    Skriver om Json filer för personalen till en csv och excel fil
    :param verbose:
    :return:
    """
    filelist = list(Path(STAFF_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
    # print(STAFF_USER_FOLDER_PATH)
    # print(STAFF_USER_XLSX_FILEPATH)
    df_list = []
    filelist_len = len(filelist)
    print_progress_bar(0, filelist_len, prefix='Staff Export Progress:', suffix='Complete', length=150)
    for i, filepath in enumerate(filelist):
        print_progress_bar(iteration=i + 1, total=filelist_len, prefix=F'Staff  Export Progress:{i}/{filelist_len}  ', suffix='Complete', length=150)

        if verbose:
            print(filepath)
        try:
            user = load_dict_from_json_path(filepath=str(filepath))
        except json.decoder.JSONDecodeError:
            print(f" error on filepath : {filepath}                         2022-09-07 15:02:33")
            raise json.decoder.JSONDecodeError(filepath)
        except Exception as e:
            print(f" error on filepath : {filepath}                         2022-09-07 15:02:27")
            raise Exception(e)
        else:
            if len(user["account_user_name"]) != 6:
                continue
            df = pd.DataFrame(user, index=range(1, len(user.keys())))
            # if verbose:
            #     print(df)
            df_list.append(df[:1])
    try:
        dfz = pd.concat(df_list, ignore_index=True, sort=False)
    except ValueError as e:
        raise ValueError(e)
    else:
        # print(".", end="")
        if verbose:
            print(dfz)
        dfz = dfz.replace(np.nan, "x", regex=True)
        dfz.to_csv(STAFF_USER_FOLDER_PATH + 'staff.csv', sep=';', encoding='utf-8', index=False)
        dfz.to_excel(STAFF_USER_XLSX_FILEPATH, sheet_name='data', index=False)

        if verbose:
            print(f"dfz {STAFF_USER_FOLDER_PATH + 'staff.csv'} complete")
        if verbose:
            print(f"dfz {STAFF_USER_XLSX_FILEPATH} complete")
        return dfz


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)
    write_student_xlsx_from_json()
    write_staff_xlsx_from_json()

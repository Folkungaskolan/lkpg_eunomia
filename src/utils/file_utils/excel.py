import json
from pathlib import Path

import numpy as np
import pandas as pd

from settings.folders import STUDENT_USER_FOLDER_PATH, STUDENT_USER_XLSX_FILEPATH, STAFF_USER_XLSX_FILEPATH, STAFF_USER_FOLDER_PATH
from utils import print_progress_bar
from utils.file_utils import load_dict_from_json_path


def write_student_xlsx_from_json(verbose: bool = False):
    if verbose:
        print("write_student_xlsx_from_json start")

    filelist = list(Path(STUDENT_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))

    df_list = []
    filelist_len = len(filelist)
    print_progress_bar(0, filelist_len, prefix='Elever Export Progress:', suffix='Complete', length=150)
    for i, filepath in enumerate(filelist):
        print_progress_bar(iteration=i + 1, total=filelist_len, prefix=F'Elever Export Progress:{i}/{filelist_len}', suffix='Complete', length=150)

        try:
            user = load_dict_from_json_path(filepath=filepath)
        except json.decoder.JSONDecodeError:
            print(f" error on filepath : {filepath}                         2022-09-07 15:04:48")
            raise json.decoder.JSONDecodeError(filepath)
        except Exception as e:
            print(f" error on filepath : {filepath}                         2022-09-07 15:04:51")
            raise Exception(e)
        else:
            df = pd.DataFrame(user, index=range(1, len(user.keys())))
            if verbose:
                print(df)
            df_list.append(df[:1])
            # print(".", end="")
            # if i % 100 == 0:
            #     print(".")
            #     print(f"{i}", end="")

    try:
        dfz = pd.concat(df_list, ignore_index=True, sort=False)
    except ValueError as e:
        raise ValueError(e)
    else:

        if verbose:
            pass
        print(dfz)
        dfz = dfz.replace(np.nan, "x", regex=True)
        dfz.to_csv(STUDENT_USER_FOLDER_PATH + 'elever.csv', sep=';', encoding='utf-8', index=False)
        dfz.to_excel(STUDENT_USER_XLSX_FILEPATH, sheet_name='data', index=False)

        nyckel_hanterings_df = dfz[[]]

        if verbose:
            print(f"dfz {STUDENT_USER_FOLDER_PATH + 'elever.csv'} complete")
        if verbose:
            print(f"dfz {STUDENT_USER_XLSX_FILEPATH} complete")
        return dfz


def write_staff_xlsx_from_json(verbose: bool = False) -> None:
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
            user = load_dict_from_json_path(filepath=filepath)
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
    write_student_xlsx_from_json(verbose=False)
    # write_staff_xlsx_from_json(verbose=False)

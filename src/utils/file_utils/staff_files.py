""" Funktioner som hanterar anställdas filer"""
import os
from pathlib import Path

from CustomErrors import NoUserFoundError
from settings.folders import STAFF_USER_FOLDER_PATH
from utils.file_utils import load_dict_from_json_path
from utils.file_utils.json_wrapper import save_dict_to_json


def find_staff_json_filepath(account_user_name: str, verbose: bool = False) -> str:
    """
    :param account_user_name: str användarens användarnamn
    :param verbose: bool  skriv ut mer info i terminalen
    :return: str  sökväg till json filen som sträng
    """
    try:
        filelist = list(Path(STAFF_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
        if verbose:
            print(F"filelist len = {len(filelist)}                                 2022-09-16 09:04:47")
        for i, filepath in enumerate(filelist):
            if verbose:
                print(F"{i}:{filepath}")
            if account_user_name in str(filepath.stem):
                if verbose:
                    print(F"hittad : {filepath}                                     2022-09-16 09:04:54")
                return str(filepath)
    except Exception as e:
        print(e)
        if verbose:
            print("2022-09-28 16:46:03")
            print(account_user_name)
            print(filepath)
        raise
    raise NoUserFoundError(F"User Json  for {account_user_name} not found")


def save_staff_as_json(account_user_name: str = None,
                       first_name: str = None,
                       last_name: str = None,
                       email: str = None,
                       mobil: str = None,
                       telefon: str = None,
                       personnummer: str = None,
                       slutdatum: str = None,
                       titel: str = None,
                       do_not_retain_old_info: bool = False,
                       verbose: bool = False, ) -> None:
    """ Sparar ny information, tar inte bort gamla värden
    :type account_user_name: str
    :type first_name: str
    :type last_name: str
    :type email: str
    :type mobil: str
    :type telefon: str
    :type personnummer: str
    :type slutdatum: str
    :type titel: str
    :type do_not_retain_old_info: bool
    :type verbose: bool
    :return: None

    :param account_user_name: användarens användarnamn
    :param first_name: förnamn för användaren
    :param last_name: efternamn för användaren
    :param email: email för användaren
    :param mobil: mobil för användaren
    :param telefon: telefon för användaren
    :param personnummer: personnummer för använd
    :param slutdatum: slutdatum för användaren
    :param titel: titel för användaren
    :param do_not_retain_old_info: bool om vi inte vill behålla gamla värden
    :param verbose: bool skriv ut mer info i terminalen
    :return: None
    """
    if account_user_name is None:
        raise ValueError("account_user_name is None")

    new_staff_dict = {
        "account_1_user_name": account_user_name,
        "account_2_first_name": first_name,
        "account_2_last_name": last_name,
        "account_3_email": email,
        "mobil": mobil,
        "telefon": telefon,
        "personnummer": personnummer,
        "email": email,
        "born_year": personnummer[:4],
        "born_month": str(int(personnummer[4:6])),  # tar bort ledande nolla om den finns
        "born_day": personnummer[6:8],
        "slutdatum": slutdatum,
        "titel": titel,
    }

    try:
        student_json_filepath = find_staff_json_filepath(account_user_name=account_user_name)
        if verbose:
            print(F"student_json_path|{student_json_filepath}")
    except NoUserFoundError:
        save_dict_to_json(data=new_staff_dict,  # No old info available, make new file
                          filepath=STAFF_USER_FOLDER_PATH + account_user_name + ".json")
    else:
        if do_not_retain_old_info:  # save file without updating, aka forget old keys
            os.remove(student_json_filepath)
            save_dict_to_json(data=new_staff_dict,
                              filepath=STAFF_USER_FOLDER_PATH + account_user_name + ".json")
            return
        old_staff_dict = load_dict_from_json_path(student_json_filepath)
        save_dict_to_json(data=old_staff_dict | new_staff_dict,  # updates old dict with new dicts values
                          filepath=STAFF_USER_FOLDER_PATH + account_user_name + ".json")


if __name__ == '__main__':
    pass

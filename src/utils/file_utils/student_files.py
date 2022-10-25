""" student relaterade funktioner """
from datetime import datetime
from pathlib import Path

from CustomErrors import NoUserFoundError
from settings.folders import STUDENT_USER_FOLDER_PATH
from utils.file_utils.json_wrapper import save_dict_to_json, load_dict_from_json_path
from utils.path_utils import delete_file


def find_student_json_filepath(account_user_name: str, verbose: bool = False) -> str:
    """
    :param account_user_name: str användarens användarnamn
    :param verbose: bool  skriv ut mer info i terminalen
    :return: str  sökväg till json filen som sträng
    """
    try:
        filelist = list(Path(STUDENT_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
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
            print("2022-09-16 09:04:00")
            print(account_user_name)
            print(filepath)
        raise
    raise NoUserFoundError(F"User Json  for {account_user_name} not found")


def save_student_as_json(account_user_name: str = None,
                         first_name: str = None,
                         last_name: str = None,
                         klass: str = None,
                         skola: str = None,
                         birthday: str = None,
                         google_pw: str = None,
                         eduroam_pw: str = None,
                         eduroam_pw_gen_datetime: datetime = None,
                         verbose: bool = False,
                         do_not_retain_old_info: bool = False,
                         this_is_a_web_import: bool = False
                         ) -> None:
    """ Sparar ny information, tar inte bort gamla värden
    :param account_user_name: användarens användarnamn
    :param first_name: förnamn för användaren
    :param last_name: efternamn för användaren
    :param klass: klass för användaren
    :param skola: skola för användaren
    :param birthday: födelsedag användaren
    :param google_pw: google lösenord användaren
    :param eduroam_pw: eduroam lösenord användaren
    :param eduroam_pw_gen_datetime: när genererades detta eduroam lösenord
    :param verbose: visa mer info i terminalen
    :param do_not_retain_old_info:
    :param this_is_a_web_import:

    :type this_is_a_web_import:
    :type do_not_retain_old_info: bool
    :return: funktionen skriver en fil till disk. Inget returneras.
    """
    if account_user_name is None:
        raise ValueError("account_user_name is None")
    if klass is None:
        klass = "undetermined_class"
    student_dict = {
        "account_1_user_name": account_user_name,
        "account_2_first_name": first_name,
        "account_2_last_name": last_name,
        "klass": klass,
        "skola": skola,
        "birthday": birthday,
        "account_3_google_pw": google_pw,
        "account_3_eduroam_pw": eduroam_pw,
        "account_3_eduroam_pw_gen_date": eduroam_pw_gen_datetime
    }
    if this_is_a_web_import:
        student_dict["student_last_import_datetime"] = datetime.now().strftime("%Y-%m-%d")

    try:
        student_json_filepath = find_student_json_filepath(account_user_name=account_user_name)
        if verbose:
            print(F"student_json_path|{student_json_filepath}")
    except NoUserFoundError:
        save_dict_to_json(data=student_dict, filepath=STUDENT_USER_FOLDER_PATH + klass + "_" + account_user_name + ".json")

    else:
        if do_not_retain_old_info:  # save file without updating, aka forget old keys
            delete_file(student_json_filepath)
            save_dict_to_json(data=student_dict, filepath=STUDENT_USER_FOLDER_PATH + klass + "_" + account_user_name + ".json")
            return
        old_dict = load_dict_from_json_path(student_json_filepath)
        if old_dict["klass"] != student_dict["klass"]:
            delete_file(student_json_filepath)
        if old_dict["account_3_eduroam_pw"] != None:
            pass
        save_dict_to_json(data=old_dict | student_dict, filepath=STUDENT_USER_FOLDER_PATH + klass + "_" + account_user_name + ".json")


if __name__ == '__main__':
    save_student_as_json(account_user_name="test1", first_name="test åäö", last_name="test3", klass="test4", skola="test5", birthday="test6", google_pw="test7")

# -*- coding: utf-8 -*-
"""
Created on 2020-08-19 15:21:23
Last update 2020-11-09 11:11:01
@author: Lyam Dolk Folkungaskolan Linköpings Kommun
@mail : lyamdolk@gmail.com
"""
import os
from datetime import datetime
from pathlib import Path

import dask
import pandas as pd
from dask import delayed
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from util import update_student_eduroam_password, get_student_user_json_obj
# from pickeling import save_obj_as_pickle #TODO rework and replace with Json
from util.web import init_firefox_webdriver
from util.web.student_interface import get_student_pw, get_single_user_from_web_to_json

from CustomErrors import LogInFailure, NoUserFoundError
from settings.folders import STUDENT_EDUROAM_GEN_FOLDER
from utils import load_dict_from_json_path

"""
https://selenium-python.readthedocs.io/installation.html
pip install selenium
https://www.selenium.dev/downloads/
https://firefox-source-docs.mozilla.org/testing/geckodriver/Support.html
Download and place driver in same folder as py script : https://github.com/mozilla/geckodriver/releases
Getting Started  https://selenium-python.readthedocs.io/getting-started.html
"""


def generate_and_save_eduroam_for_user(account_user_name: str, headless_input_bool: bool = True) -> None:
    """    Skapar eduroam användare    """
    print(F"start {account_user_name=} ")
    # initiera drivaren
    try:
        user = get_student_user_json_obj(account_user_name=account_user_name)
    except NoUserFoundError:
        get_single_user_from_web_to_json(account_user_name=account_user_name)
        user = get_student_user_json_obj(account_user_name=account_user_name)
    driver = init_firefox_webdriver(
        headless_bool=headless_input_bool)  # behöver vara firefox för att kringgå problem med redan inloggad användare
    # Hämta sidan
    driver.get(url="https://itsupport.linkoping.se/form/eduroam")
    # Fyll i uppgifterna
    user_input = driver.find_element(By.NAME, "name")  # hitta vart användarnamnet ska in
    # user_input = driver.find_element_by_name("name")  # hitta vart användarnamnet ska in
    user_input.clear()  # töm rutan
    user_input.send_keys(account_user_name)  # fyll i användarnamnet
    pass_input = driver.find_element(By.NAME, "pswd")  # hitta vart lösenordet ska in
    pass_input.clear()  # töm rutan
    pass_input.send_keys(user["account_3_google_pw"])  # fyll i lösenordet
    user_input.send_keys(Keys.RETURN)  # tryck på "enter" när allt är ifyllt

    # inloggning klar
    try:
        new_pass_button = WebDriverWait(driver, 60 * 3).until(
            expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/form/input")))
        # vänta på att sidan laddas, sen hämta vart knappen för "generera nytt lösenord" är
    except TimeoutException:
        driver.close()
        raise LogInFailure
    else:
        new_pass_button.click()  # klicka på knappen

        # user och lösen genererat
        eduroam_user = WebDriverWait(driver, 4 * 60).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "/html/body/div/div[2]/p[7]/span")))  # hämta eduroam användaren
        eduroam_pass = driver.find_element(By.XPATH, "/html/body/div/div[2]/p[8]/span")  # hämta Lösen
        edu_roam_credentials = {"anv_namn": eduroam_user.text,
                                "pw": eduroam_pass.text
                                }  # skicka ut anv och lösen
        driver.close()  # Stäng fönstret
        update_student_eduroam_password(account_user_name=account_user_name, new_eduroam_password=eduroam_pass.text)


def gen_and_print_eduroam(user: dict, pw: str, klass: str, headless_input_bool: bool = True) -> bool:
    """     generera eduroam lösenorden och markera användaren för utskrift.    """
    anv_namn = user["account_1_user_name"].strip()
    pw = user["account_1_user_name"].strip()
    try:
        generate_and_save_eduroam_for_user(account_user_name=anv_namn, pw=pw, headless_input_bool=headless_input_bool)
    except LogInFailure:
        return False
    else:
        return True


def generate_and_print_eduroam_creds_from_pickle(account_user_name: str, pw: str = None, headless_input_bool: bool = True) -> tuple[
    bool, str, str, str]:
    """     Generera eduroam lösenorden och markera användaren för utskrift.    """
    account_user_name = account_user_name.strip()
    if pw is None:
        pw = get_student_pw(account_user_name=account_user_name)
    try:
        generate_and_save_eduroam_for_user(account_user_name=account_user_name, pw=pw, headless_input_bool=headless_input_bool)
    except LogInFailure:
        print(F"Eduroam generering för användare : {account_user_name} misslyckades")


def append_to_file(account_user_name: str, pw: str, eduroam_pw: str = None) -> None:
    """
    Sparar resultat till fil
    :param account_user_name:Str
    :param pw:Str
    :param eduroam_pw:Str
    """
    now = datetime.now()
    user = {}
    user["anv_namn"] = account_user_name
    user["pw"] = pw
    user["edu_pw"] = now.strftime("%Y-%d-%m_%H:%M")
    user["edu_pw_gen_date"] = now.strftime("%Y-%d-%m_%H:%M")
    print(f"{account_user_name=}|{pw=}|{eduroam_pw=}")
    if pw != "inloggning misslyckades":
        update_student_eduroam_password(account_user_name=account_user_name, new_eduroam_password=eduroam_pw)


def get_files_in_folder(path: str, extension: str = ".pkl") -> list[str]:
    file_list = []
    for file in os.listdir(path):
        if file.endswith(extension):
            file_path = os.path.join(path, file)
            file_list.append(file_path)
    return file_list


def a1_split_csv_classfiles_to_pickles(path: str) -> None:
    results = []
    for file in os.listdir(path):
        if file.endswith(".csv"):
            if "_FOL" in file:
                results.append(delayed(a3_split_single_csv_to_pickles)(file, path))
    dask.compute(results)


def a3_split_single_csv_to_pickles(file: str, path: str) -> bool:
    """ Delar csvfiler från elevhanteraren till pickels för vidare hantering
    och generering"""
    filepath = os.path.join(path, file)
    print(f"splitting {filepath} into pickles")
    df = pd.read_csv(filepath, encoding="latin1")
    print(df.columns)
    for label, row_df in df.iterrows():
        user = {"anv_namn": row_df["Kontonamn"], "pw": row_df["Lösenord"], "klass": file.split(".")[0]}
        save_obj_as_pickle(dict_obj=user, folder_path=path, filename=row_df["Kontonamn"])
    # os.remove(filepath)
    return True


def gen_from_json(filepath: str, headless_input_bool: bool = True) -> bool:
    user = load_dict_from_json_path(folder_path=filepath)
    success = gen_and_print_eduroam(user=user, headless_input_bool=headless_input_bool)
    if not success:
        os.remove(filepath)
        return True
    else:
        return False


def gen_pickles_in_folder(path: str, i: int = 1, max_iterations: int = 2, infinite_loop=False) -> None:
    while (max_iterations > i and len(list(Path(STUDENT_EDUROAM_GEN_FOLDER).rglob('*.[Jj][Ss][Oo][Nn]'))) > 0) \
            or (infinite_loop and len(list(Path(STUDENT_EDUROAM_GEN_FOLDER).rglob('*.[Jj][Ss][Oo][Nn]'))) > 0):
        print(F"path | iter ={i}")
        gen_list = list(Path(path).rglob('*.[Jj][Ss][Oo][Nn]'))
        print("gen_list", end=": ")
        print(gen_list)
        proccess_results = []
        for filepath in gen_list:
            proccess_results.append(delayed(gen_from_json)(filepath))
        dask.compute(proccess_results)
        print("dask complete")
        print(proccess_results)
        i = i + 1


def folder_cleanup(path: str, anv_name: str) -> bool:
    files = get_files_in_folder(path, extension=".txt")
    for file in files:
        if anv_name in file and "fail" in file:
            os.remove(os.path.join(path, file))


def split_klass_csv_to_student_gen_pickles(from_csv_path: str, student_gen_path: str) -> None:
    print("START  split_klass_csv_to_student_gen_pickles")
    print(F"CSV path: {from_csv_path}")
    print(F"results path: {student_gen_path}")
    for file in os.listdir(from_csv_path):
        if file.endswith(".csv"):
            filepath = os.path.join(from_csv_path, file)
            print(f"splitting {filepath} into pickles")
            df = pd.read_csv(filepath, encoding="latin1")
            # print(df.columns)
            for label, row_df in df.iterrows():
                user = {"anv_namn": row_df["Kontonamn"],
                        "pw": row_df["Lösenord"],
                        "klass": file.split(".")[0]}
                save_obj_as_pickle(dict_obj=user, folder_path=student_gen_path + user["klass"] + "/", filename=row_df["Kontonamn"])
            os.rename(from_csv_path + file, from_csv_path + "done/" + file)
    print("END  split_klass_csv_to_student_gen_pickles")
    print("--------------------------------------------------")


def append_edu_info_to_student_pickle(anvnamn: str, pw: str, edu_pw: str) -> None:
    user = {}
    now = datetime.now()
    user["anv_namn"] = anvnamn
    user["pw"] = pw
    user["edu_pw"] = edu_pw
    user["edu_pw_gen_date"] = now.strftime("%Y-%m-%d_%H:%M")
    update_student_eduroam_password(account_user_name=anvnamn, new_eduroam_password=edu_pw)


def rensa_gen_mapp():  # TODO
    path = "H:/Min enhet/Python temp/e2.eduroam_student_gen_pickles/"
    filelist = list(Path(path).rglob('*.[Pp][Kk][Ll]'))
    folder_list = []
    for filepath in filelist:
        folder_name = os.path.basename(os.path.dirname(filepath))
        if folder_name not in folder_list:
            folder_list.append(folder_name)
    print(folder_list)


if __name__ == "__main__":
    # copy_pickle_to_eduroam_gen_folder(anv_namn="hannor653")
    gen_pickles_in_folder(path="H:/Min enhet/Python temp/e2.eduroam_student_gen_pickles/",
                          max_iterations=2,
                          infinite_loop=False)

    # append_edu_info_to_student_pickle(anvnamn="zoenit692", edu_pw="sczhrbpw")

    # gen_and_print_eduroam_from_pickle(anv_namn="angisa418", pw=None)
    # gen_and_print_eduroam_from_pickle(anv_namn="zoenit692", pw="rpdcftkb")

    # Uppdatera Google filer mha CoLab
    # https://colab.research.google.com/drive/15YSCsSWbU8oykg6nXGtLFkBailxJxxV1#scrollTo=QPhYf-UCn083&uniqifier=1
    # gen_and_print_eduroam_from_pickle(anv_namn="versam596", pw=None)

    move_pickles_to_root_of_gen_folders()
    rensa_tomma_mappar_i_gen_mapp()

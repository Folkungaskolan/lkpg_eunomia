import concurrent
import concurrent.futures
import json
import math
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import selenium
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from CustomErrors import NoUserFoundError
from settings.folders import WEB_ID_TO_PROCESS_PATH, STUDENT_USER_FOLDER_PATH
from settings.threadsettings import THREADCOUNT
from utils.creds import get_cred
from utils.decorators import function_timer
from utils.file_utils import save_student
from utils.file_utils.json_wrapper import load_dict_from_json_path
from utils.path_utils.path_helpers import split_file_name_no_suffix_from_filepath, split_student_account_user_name_from_filepath
from utils.web_utils.general_web import init_chrome_webdriver, position_windows


def fetch_single_student_from_web(account_user_name: str, headless_input_bool: bool = False) -> dict[str:str]:
    """ import a student from the web to a json file"""
    if account_user_name is None:
        raise ValueError("account_user_name is None")
    driver = init_chrome_webdriver(headless_bool=headless_input_bool)
    if not headless_input_bool:
        position_windows(driver=driver)
    driver.get(url="https://elevkonto.linkoping.se/")
    driver = login_student_accounts_page(driver)
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/div/article/section/form/div/div/div[1]/div/div[2]/div/select/option[2]")))
    driver.get(url=f"https://elevkonto.linkoping.se/users?FreeText={account_user_name}")
    rows = driver.find_elements(by=By.CLASS_NAME, value="item-row")
    for row in rows:
        data_item_id = row.get_attribute("data-item-id")
        print(data_item_id)
        if data_item_id is not None:
            driver.get(url=F"https://elevkonto.linkoping.se/entity/view/user/{data_item_id}")
            try:
                # account_user_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[2]/div[2]/span").text
                birthday = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[1]/div[2]/span").text
                first_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[7]/div[2]/span").text
                last_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[8]/div[2]/span").text
                klass = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[13]/div[2]/span").text
                skola = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[10]/div[2]/span").text
            except selenium.common.exceptions.NoSuchElementException as e:
                print(f" proccess failed id:{id}")
                raise NoUserFoundError(f"no user found with id:{id} | account_user_name:{account_user_name}")
            try:
                pw = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[5]/div[2]/span").text
            except selenium.common.exceptions.NoSuchElementException as e:
                print(f" proccess failed id:{id} no pw found for user : {account_user_name}")
                raise NoUserFoundError(f"no user found with id:{id} | account_user_name:{account_user_name}")
            else:
                driver.close()
                return {"account_user_name": account_user_name,
                        "first_name": first_name,
                        "last_name": last_name,
                        "klass": klass,
                        "skola": skola,
                        "birthday": birthday,
                        "google_pw": pw}
    raise NoUserFoundError(f"no user found with id:{id} | account_user_name:{account_user_name}")


def login_student_accounts_page(driver):
    """
    login to the student accounts page  https://elevkonto.linkoping.se/
    :param driver:
    :type driver:
    :return:
    :rtype:
    """
    driver.get(url="https://elevkonto.linkoping.se/")
    creds = get_cred(account_file_name="lyam_windows_user")
    user_name = creds["usr"]
    pw = creds["pw"]

    user_input = driver.find_element(By.NAME, "Username")  # hitta vart anv??ndarnamnet ska in
    user_input.send_keys(user_name)
    pass_input = driver.find_element(By.NAME, "Password")  # hitta vart l??senordet ska in
    pass_input.clear()  # t??m rutan
    pass_input.send_keys(pw)  # fyll i l??senordet
    pass_input.send_keys(Keys.RETURN)
    return driver


def save_student_id_from_url(driver, url: str):
    """ H??mtar student ID f??r varje elev fr??n klass sidan """

    driver.get(url=url)
    rows = driver.find_elements(by=By.CLASS_NAME, value="item-row")
    for row in rows:
        data_item_id = row.get_attribute("data-item-id")
        # print(data_item_id)
        if data_item_id is not None:
            item_id = {"data_item_id": data_item_id}
            with open(WEB_ID_TO_PROCESS_PATH + data_item_id + '.json', 'w') as f:
                json.dump(item_id, f)
            f.close()
    return driver


@function_timer
def _1_create_students_ids_from_web(run_only_class: list[str] = None, force_single_thread: bool = False, headless_bool: bool = True) -> None:
    """
    ??ppnar Elevkonto sidan
    Listar skolor i Skola
    F??r varje skola
        Listar klasser i specifik skola
        Skickar klass lista till funktion som drar Student id fr??n hemsidan till pickles
    :return:
    """
    driver = init_chrome_webdriver(headless_bool=headless_bool)
    driver = login_student_accounts_page(driver)
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/div/article/section/form/div/div/div[1]/div/div[2]/div/select/option[2]")))
    school_selector = Select(driver.find_element(By.ID, "field-School"))
    skol_lista = []
    klasser = {}
    for option in school_selector.options:
        skol_lista.append(option.text)
    print(skol_lista)
    urls = []
    for skola in skol_lista[1:]:
        if skola in ["Folkungaskolan 3"]:  # Hoppas ??ver
            # if skola in ["Folkungaskolan 3", 'S:t Lars gymnasium 1']:  # Hoppas ??ver
            continue
        school_selector.select_by_visible_text(skola)
        time.sleep(1)
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/article/section/form/div/div/div[1]/div/div[3]/div/select/option[2]")))
        class_selector = Select(driver.find_element(By.ID, "field-SchoolClass"))
        for option in class_selector.options[1:]:
            url_skola = skola.replace(" ", "+").replace(":", "%3A")
            if run_only_class is None:
                urls.append(F'https://elevkonto.linkoping.se/users?FreeText=&School={url_skola}&SchoolClass={option.text}')
                urls.append(F'https://elevkonto.linkoping.se/users?FreeText=&School={url_skola}&SchoolClass={option.text}&_page=2')
            elif option.text in run_only_class:
                urls.append(F'https://elevkonto.linkoping.se/users?FreeText=&School={url_skola}&SchoolClass={option.text}')
                urls.append(F'https://elevkonto.linkoping.se/users?FreeText=&School={url_skola}&SchoolClass={option.text}&_page=2')
    print("Run END")
    driver.close()
    print(urls)
    if force_single_thread:
        _2_1_process_id_into_student_record(urls=urls, headless_bool=headless_bool)
    else:
        sublists = list(split(urls, chunk_size=THREADCOUNT))
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADCOUNT) as executor:
            results = [executor.submit(_1_2_rips_ids_from_urls, urls=sublist, thread_nr=i) for i, sublist in enumerate(sublists)]

        for f in concurrent.futures.as_completed(results):
            print(f.result())


@function_timer
def _1_2_rips_ids_from_urls(urls: list[str], headless_bool: bool = True, thread_nr: int = 0) -> None:
    driver = init_chrome_webdriver(headless_bool=headless_bool)
    driver = login_student_accounts_page(driver)
    if not headless_bool:
        position_windows(driver=driver, position_nr=(thread_nr % 4) + 1)
    for url in urls:
        print(url)
        driver = save_student_id_from_url(driver, url=url)
    driver.close()
    return F"Thread {thread_nr} done"


@function_timer
def _2_process_id_into_student_record(verbose: bool = False, force_single_thread: bool = False, headless_bool: bool = False) -> None:
    """ H??mta id json filer och h??mta elev f??r varje s??dan"""
    if verbose:
        print(F"process_student_ids starting")
    filelist = list(Path(WEB_ID_TO_PROCESS_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
    print(F"len {len(filelist)}:filelist")
    if force_single_thread:
        _2_1_process_id_into_student_record(id_list=filelist, verbose=verbose, headless_bool=headless_bool)
    else:
        sublists = list(split(filelist, chunk_size=math.ceil(len(filelist) / THREADCOUNT)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADCOUNT) as executor:
            results = [executor.submit(_2_1_process_id_into_student_record, id_list=sublist, thread_nr=i) for i, sublist in enumerate(sublists)]

        for f in concurrent.futures.as_completed(results):
            print(f.result())


def split(list_a, chunk_size):
    """ Delar listan i delar s?? tr??darna f??r varsin del"""
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]


def _2_1_process_id_into_student_record(id_list: list[str], verbose: bool = False, headless_bool: bool = True, thread_nr: int = 0) -> None:
    """ Threaded student fetcher """
    # print(F"process_student_ids starting in thread {thread_nr}")
    # print(F"t:{thread_nr} idlist: {id_list}")
    # print(F"t:{thread_nr} len {len(id_list)}:")
    driver = init_chrome_webdriver(headless_bool=headless_bool)
    if not headless_bool:
        position_windows(driver=driver, position_nr=(thread_nr % 4) + 1)
    driver = login_student_accounts_page(driver)
    for id_file in id_list:
        student_web_id = split_file_name_no_suffix_from_filepath(id_file)

        driver.get(url=F"https://elevkonto.linkoping.se/entity/view/user/{student_web_id}")
        try:
            account_user_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[2]/div[2]/span").text
            birthday = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[1]/div[2]/span").text
            first_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[7]/div[2]/span").text
            last_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[8]/div[2]/span").text
            klass = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[13]/div[2]/span").text
            skola = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[10]/div[2]/span").text
        except selenium.common.exceptions.NoSuchElementException as e:
            print(f" process failed id:{student_web_id}")
            continue
        try:
            google_pw = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[5]/div[2]/span").text
        except selenium.common.exceptions.NoSuchElementException as e:
            print(f" process failed id:{student_web_id} no pw found for user : {account_user_name}")
            continue
        else:
            print(F"t:{thread_nr} processing id:{student_web_id} -> {account_user_name}          2022-10-25 11:06:03")
            save_student(user_id=account_user_name, first_name=first_name, last_name=last_name, klass=klass, birthday=birthday, google_pw=google_pw,
                         skola=skola, this_is_a_web_import=True)
            os.remove(id_file)
    return f"Done in thread {thread_nr}"


@function_timer
def run_id_import(run_only_class: list[str] = None, headless_bool: bool = False):
    """ Run all steps to import student ids from web """
    if run_only_class is None:
        _1_create_students_ids_from_web(headless_bool=headless_bool)
    else:
        _1_create_students_ids_from_web(run_only_class=run_only_class, headless_bool=headless_bool)


@function_timer
def import_all_student_from_web() -> None:
    """ Importera alla elever fr??n webben """
    _1_create_students_ids_from_web()
    _2_process_id_into_student_record()


@function_timer
def check_old_files(new_file_within_days_limit: int = None) -> None:
    """ Kolla om det finns gamla filer kvar i mappen """
    filelist = list(Path(STUDENT_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
    old_files = []
    if new_file_within_days_limit is None:
        NOW = datetime.now()
    else:
        NOW = datetime.now() - timedelta(days=new_file_within_days_limit)
    for file in filelist:
        change_date: datetime = datetime.fromtimestamp(os.path.getmtime(file))
        if change_date.date() != NOW.date():
            old_files.append(file)  # files older than today
    fetched_students = {}
    print(f"{len(old_files)} old files found")
    for filepath in old_files:
        if "vikjon742" not in str(filepath):
            continue
        print(f"processing file: {filepath}")
        user_name = split_student_account_user_name_from_filepath(filepath)
        duplicate_files = []
        try:
            if user_name in fetched_students.keys():
                user = fetch_single_student_from_web(account_user_name=user_name)
                print(user)
        except NoUserFoundError as e:
            print(F"user not found {user_name}")
            os.rename(filepath, F"{STUDENT_USER_FOLDER_PATH}oldstudent_{user_name}.json")
            continue
        for file in filelist:
            if split_student_account_user_name_from_filepath(file) == user_name:
                duplicate_files.append(file)
        print(F"duplicate_files{duplicate_files}")
        for file in duplicate_files:
            print(F"dup file :  file {file}", end=" ")
            user = load_dict_from_json_path(file)
            print(user.get("account_3_eduroam_pw", -1))
            if user.get("account_3_eduroam_pw", -1) == -1:
                print("removing file")
                os.remove(file)
            else:
                eduroam_pw = user.get("account_3_eduroam_pw")
                eduroam_pw_gen_date = user.get("account_3_eduroam_pw_gen_date")
                os.remove(file)
                save_student(user_id=fetched_students.get("account_user_name"),
                             first_name=user.get("first_name"),
                             last_name=user.get("last_name"),
                             klass=user.get("klass"),
                             skola=user.get("skola"),
                             birthday=user.get("birthday"),
                             google_pw=user.get("google_pw"),
                             eduroam_pw=eduroam_pw,
                             eduroam_pw_gen_datetime=eduroam_pw_gen_date.replace("_", " "),
                             this_is_a_web_import=True)
                continue


if __name__ == "__main__":
    # _1_create_students_ids_from_web(run_only_class=["EK20B_FOL"], headless_bool=False)
    # import_all_student_from_web()
    # _2_process_id_into_student_record()

    # import_single_student_from_web(account_user_name="vikjon742", headless_input_bool=False)
    pass

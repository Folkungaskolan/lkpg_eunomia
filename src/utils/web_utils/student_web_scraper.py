import concurrent
import concurrent.futures
import json
import math
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import random

import selenium
import sqlalchemy
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy.orm import Session

from CustomErrors import NoUserFoundError
from database.models import Student_id_process_que_dbo
from database.mysql_db import init_db, MysqlDb
from settings.folders import STUDENT_USER_FOLDER_PATH
from settings.threadsettings import THREADCOUNT
from utils.creds import get_cred
from utils.decorators import function_timer
from utils.file_utils import save_student
from utils.file_utils.to_csv import write_student_csv_from_mysql
from utils.file_utils.json_wrapper import load_dict_from_json_path
from utils.path_utils.path_helpers import split_student_account_user_name_from_filepath
from utils.print_progress_bar import print_progress_bar

from utils.student.student_mysql import save_student_information_to_db, count_student
from utils.web_utils.general_web import init_chrome_webdriver, position_windows


def fetch_single_student_from_web(account_user_name: str, headless_input_bool: bool = False) -> dict[str:str]:
    """ import a student from the web to a json file"""
    if account_user_name is None:
        raise ValueError("account_user_name is None")
    s = MysqlDb().session()
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
                save_student_information_to_db(account_user_name=account_user_name,
                                               first_name=first_name,
                                               last_name=last_name,
                                               klass=klass,
                                               skola=skola,
                                               birthday=birthday,
                                               google_pw=pw,
                                               session=s)
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

    user_input = driver.find_element(By.NAME, "Username")  # hitta vart användarnamnet ska in
    user_input.send_keys(user_name)
    pass_input = driver.find_element(By.NAME, "Password")  # hitta vart lösenordet ska in
    pass_input.clear()  # töm rutan
    pass_input.send_keys(pw)  # fyll i lösenordet
    pass_input.send_keys(Keys.RETURN)
    return driver


@function_timer
def _1_create_student_ids_from_web(run_only_class: list[str] = None,
                                   force_single_thread: bool = False,
                                   headless_bool: bool = True) -> None:
    """
    Öppnar Elevkonto sidan
    Listar skolor i Skola
    För varje skola
        Listar klasser i specifik skola
        Skickar klass lista till funktion som drar Student id från hemsidan till pickles
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
        if skola in ["Folkungaskolan 3"]:  # Hoppas över
            # if skola in ["Folkungaskolan 3", 'S:t Lars gymnasium 1']:  # Hoppas över
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
    print("listing urls finnished                                    2022-10-27 11:23:11")
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
def _1_2_rips_ids_from_urls(urls: list[str], headless_bool: bool = True, thread_nr: int = 0) -> str:
    driver = init_chrome_webdriver(headless_bool=headless_bool)
    driver = login_student_accounts_page(driver)
    local_session = init_db()
    if not headless_bool:
        position_windows(driver=driver, position_nr=(thread_nr % 4) + 1)
    for url in urls:
        print(f"thread:{thread_nr} {url:}")
        driver.get(url=url)
        rows = driver.find_elements(by=By.CLASS_NAME, value="item-row")
        for row in rows:
            data_item_id = row.get_attribute("data-item-id")
            if data_item_id is not None:
                item = Student_id_process_que_dbo(web_id=data_item_id)
                local_session.add(item)
    local_session.commit()
    local_session.close()
    driver.close()
    return F"Thread {thread_nr} done"


def _2_process_id_into_student_record(verbose: bool = False,
                                      force_single_thread: bool = False,
                                      headless_bool: bool = False) -> None:
    """ Hämta id json filer och hämta elev för varje sådan"""
    if verbose:
        print(F"process_student_ids starting")

    local_session = init_db()
    local_session.execute("UPDATE eunomia.student_id_process_que_dbo SET taken = 0")
    local_session.commit()

    if force_single_thread:
        _2_1_process_id_into_student_record(headless_bool=headless_bool)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADCOUNT) as executor:
            results = [executor.submit(_2_1_process_id_into_student_record, thread_nr=i) for i in range(THREADCOUNT)]
        print(F"started {len(results)} threads")
        for f in concurrent.futures.as_completed(results):
            print(f.result())
    write_student_csv_from_mysql()


def split(list_a, chunk_size):
    """ Delar listan i delar så trådarna får varsin del"""
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]


# @function_timer
def _2_1_process_id_into_student_record(headless_bool: bool = True, thread_nr: int = 0) -> str:
    """ Threaded student fetcher """
    driver = init_chrome_webdriver(headless_bool=headless_bool)
    s = init_db()
    driver = login_student_accounts_page(driver)
    if not headless_bool:
        position_windows(driver=driver, position_nr=(thread_nr % 4) + 1)
    i = 0
    if thread_nr == 0:
        start_count = s.query(Student_id_process_que_dbo).count()
        print_progress_bar(0, start_count, prefix='Progress:', suffix='Complete', length=50)
    while s.query(Student_id_process_que_dbo).count() > 0:
        i += 1
        left_count = s.query(Student_id_process_que_dbo).count()
        if left_count < 20 and thread_nr > 4:
            return f"Done in thread {thread_nr}"
        if thread_nr == 0:
            print_progress_bar(iteration=start_count - left_count,
                               total=start_count,
                               prefix='Progress:',
                               suffix=F'Complete {left_count} students left to process',
                               length=50)
        rows_remaining = s.query(Student_id_process_que_dbo.id).limit(500).all()
        thread_picked_row_id = random.choice([item for sublist in list(rows_remaining) for item in sublist])
        s.execute(f"UPDATE eunomia.student_id_process_que_dbo SET taken = 1 WHERE id = {thread_picked_row_id}")
        s.commit()
        row = s.query(Student_id_process_que_dbo).filter(Student_id_process_que_dbo.id == thread_picked_row_id).first()
        driver.get(url=F"https://elevkonto.linkoping.se/entity/view/user/{row.web_id}")
        google_pw = ""
        try:
            account_user_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[2]/div[2]/span").text
            birthday = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[1]/div[2]/span").text
            first_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[7]/div[2]/span").text
            last_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[8]/div[2]/span").text
            klass = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[13]/div[2]/span").text
            skola = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[10]/div[2]/span").text
            if klass == "ALV1214TEX04S":  # Av någon anledning får jag Anna Alkenius vuxen konto med i våra listor. Skippar den.
                s.delete(row)
                s.commit()
                continue
        except selenium.common.exceptions.NoSuchElementException as e:
            print(f" process failed id:{row.web_id}")

            continue

        try:
            google_pw = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[5]/div[2]/span").text
        except selenium.common.exceptions.NoSuchElementException as e:
            print(f" process failed id:{row.web_id} no pw found for user : {account_user_name}")
            continue
        else:
            # print(F"t:{thread_nr} processing id:{row.web_id} -> {account_user_name}          2022-10-25 11:06:03")
            save_student_information_to_db(user_id=account_user_name,
                                           first_name=first_name,
                                           last_name=last_name,
                                           klass=klass,
                                           skola=skola,
                                           birthday=birthday,
                                           google_pw=google_pw,
                                           session=s,
                                           webid=row.web_id)
            try:
                s.delete(row)
                s.commit()
            except sqlalchemy.orm.exc.ObjectDeletedError:  # happens in the end when all threads are done and they take the last same row
                pass
            continue
        return f"Done in thread {thread_nr}"


@function_timer
def run_id_import(run_only_class: list[str] = None, headless_bool: bool = False):
    """ Run all steps to import student ids from web """
    if run_only_class is None:
        _1_create_student_ids_from_web(headless_bool=headless_bool)
    else:
        _1_create_student_ids_from_web(run_only_class=run_only_class, headless_bool=headless_bool)


@function_timer
def import_all_student_from_web() -> None:
    """ Importera alla elever från webben """
    _1_create_student_ids_from_web()
    _2_process_id_into_student_record()
    count_student()
    write_student_csv_from_mysql()


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


def test():
    s = MysqlDb().session()
    # student_ids = s.query(Student_id_process_que_dbo).count()

    # s.commit()
    # print(student_ids)


if __name__ == "__main__":
    # _1_create_students_ids_from_web(run_only_class=["EK20B_FOL"], headless_bool=False)
    # import_all_student_from_web()
    # _2_process_id_into_student_record()
    # _1_create_student_ids_from_web(headless_bool=False)
    # _2_process_id_into_student_record(force_single_thread=True, headless_bool=False) # Dev version
    _2_process_id_into_student_record()  # Run version
    count_student()
    write_student_csv_from_mysql()
    # find_and_move_old_students() # kör bara om importen är helt lyckad. Dvs alla klasser alla elever hämtat från webben
    pass

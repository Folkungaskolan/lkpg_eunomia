import json
import time
from pathlib import Path

import selenium
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from settings.folders import WEB_ID_TO_PROCESS_PATH
from utils.creds import get_cred
from utils.file_utils import save_student_as_json
from utils.web_utils.general_web import init_chrome_webdriver, position_windows


def import_single_student_from_web(account_user_name: str, headless_input_bool: bool = False) -> None:
    """ import a student from the web to a json file"""
    if account_user_name is None:
        raise ValueError("account_user_name is None")
    # TODO write import_student_from_web method
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
                skola = "Folkungaskolan"
            except selenium.common.exceptions.NoSuchElementException as e:
                print(f" proccess failed id:{id}")
                continue
            try:
                pw = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[5]/div[2]/span").text
            except selenium.common.exceptions.NoSuchElementException as e:
                print(f" proccess failed id:{id} no pw found for user : {account_user_name}")
                continue
            else:
                save_student_as_json(account_user_name=account_user_name,
                                     first_name=first_name,
                                     last_name=last_name,
                                     klass=klass,
                                     skola=skola,
                                     birthday=birthday,
                                     google_pw=pw)
                s.save()
                continue
    driver.close()


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


def _2_move_students_to_old_folder() -> None:
    """ Generera eleven för respektive id """
    pass


def save_student_id_from_url(driver, url: str):
    """ Hämtar student ID för varje elev från klass sidan """

    driver.get(url=url)
    rows = driver.find_elements(by=By.CLASS_NAME, value="item-row")
    for row in rows:
        data_item_id = row.get_attribute("data-item-id")
        print(data_item_id)
        if data_item_id is not None:
            item_id = {"data_item_id": data_item_id}
            with open(WEB_ID_TO_PROCESS_PATH + data_item_id + '.json', 'w') as f:
                json.dump(item_id, f)
            f.close()
    return driver


def _1_create_students_ids_from_web(run_only_class: list[str] = None, headless_bool: bool = True) -> None:
    """
    Öppnar Elevkonto sidan
    Listar skolor i Skola
    För varje skola
        Listar klasser i specifik skola
        Skickar klass lista till funktion som drar Student id från hemsidan till pickles
    :return:
    """
    driver = init_chrome_webdriver(headless_bool=headless_bool)
    driver.get(url="https://elevkonto.linkoping.se/")

    driver = login_student_accounts_page(driver)

    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/div/article/section/form/div/div/div[1]/div/div[2]/div/select/option[2]")))

    school_selector = Select(driver.find_element(By.ID, "field-School"))

    skol_lista = []
    klasser = {}
    for option in school_selector.options:
        skol_lista.append(option.text)
    print(skol_lista)
    for skola in skol_lista[1:]:
        if skola in ["Folkungaskolan 3"]:  # Hoppas över
            # if skola in ["Folkungaskolan 3", 'S:t Lars gymnasium 1']:  # Hoppas över
            continue
        klass_lista = []
        school_selector.select_by_visible_text(skola)
        time.sleep(1)
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/article/section/form/div/div/div[1]/div/div[3]/div/select/option[2]")))
        class_selector = Select(driver.find_element(By.ID, "field-SchoolClass"))
        for option in class_selector.options[1:]:
            if run_only_class is None:
                klass_lista.append(option.text)
            elif option.text in run_only_class:
                klass_lista.append(option.text)

        klasser[skola] = klass_lista
    print(klasser)
    _1_1_rip_student_ids_from_pages(klasser=klasser)
    print("Run END")
    driver.close()


def _1_1_rip_student_ids_from_pages(klasser: str, headless_bool: bool = False, verbose: bool = False) -> None:
    """ create id json file for each student in classes"""

    if verbose:
        print(F"process_web_klass_to_u0_id_json  starting")
    driver = init_chrome_webdriver(headless_bool=headless_bool)
    driver.get(url="https://elevkonto.linkoping.se/")
    driver = login_student_accounts_page(driver)
    print(klasser)
    for skola in klasser.keys():
        print(skola)
        skola_url = skola.replace(" ", "+")
        for klass in klasser[skola]:
            # if "22" not in klass:
            #     continue
            print("Processing klass:" + klass)
            driver = save_student_id_from_url(driver=driver, url=F"https://elevkonto.linkoping.se/users?FreeText=&School={skola_url}&SchoolClass={klass}")
            driver = save_student_id_from_url(driver=driver, url=F"https://elevkonto.linkoping.se/users?FreeText=&School={skola_url}&SchoolClass={klass}&_page=2")


def _3_process_id_into_student_record(verbose: bool = False, headless_bool: bool = False) -> None:
    """ Hämta id json filer och hämta elev för varje sådan"""
    if verbose:
        print(F"process_student_ids starting")
    filelist = list(Path(WEB_ID_TO_PROCESS_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
    print(filelist)


def _3_1_process_id_into_student_record(id_list: list[str], verbose: bool = False, headless_bool: bool = True, thread_nr: int = 0) -> None:
    """ Threaded student fetcher """
    print(F"process_student_ids starting in thread {thread_nr}")
    print(F"t:{thread_nr} idlist: {id_list}")
    # driver = init_chrome_webdriver(headless_bool=headless_bool)
    # position_windows(driver=driver, position_nr=thread_nr)
    # driver = login_student_accounts_page(driver)

    # for filepath in filelist:
    #     if verbose:
    #         print(F"processing {filepath}")
    #     with open(filepath, 'r') as f:
    #         data = json.load(f)
    #     f.close()
    #     id = data["data_item_id"]
    #     user = {}
    #     driver.get(url=F"https://elevkonto.linkoping.se/entity/view/user/{id}")
    #     try:
    #         user["account_1_user_name"] = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[2]/div[2]/span").text
    #         user["birthday"] = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[1]/div[2]/span").text
    #         user["account_2_first_name"] = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[7]/div[2]/span").text
    #         user["account_2_last_name"] = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[8]/div[2]/span").text
    #         user["klass"] = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[13]/div[2]/span").text
    #         user["skola"] = "Folkungaskolan"
    #     except selenium.common.exceptions.NoSuchElementException as e:
    #         print(f" process failed id:{id}")
    #         continue
    #     try:
    #         user["account_3_google_pw"] = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[5]/div[2]/span").text
    #     except selenium.common.exceptions.NoSuchElementException as e:
    #         print(f" process failed id:{id} no pw found for user : {user['anv_namn']}")
    #         continue
    #     else:
    #         save_student(student_dict=user, verbose=verbose)  # spara eduroam lösenordet
    #         os.remove(filepath)
    #         continue


def run_id_import(run_only_class: list[str] = None, headless_bool: bool = False):
    """ Run all steps to import student ids from web """
    if run_only_class is None:
        _1_create_students_ids_from_web(headless_bool=headless_bool)
    else:
        _1_create_students_ids_from_web(run_only_class=run_only_class, headless_bool=headless_bool)


def import_all_student_from_web() -> None:
    """ Importera alla elever från webben """
    _1_1_rip_student_ids_from_pages()
    _2_move_students_to_old_folder()
    _3_1_process_id_into_student_record()


if __name__ == "__main__":
    # _1_create_students_ids_from_web(run_only_class=["EK20B_FOL"], headless_bool=False)
    _2_move_students_to_old_folder()
    _3_process_id_into_student_record(verbose=True, headless_bool=False)
    pass

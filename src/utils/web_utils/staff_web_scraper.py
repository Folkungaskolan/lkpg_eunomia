""" Hanterar personal relaterade funktioner. Hämtar informatin om personal från webbplatsen >>> HTML """
from selenium import webdriver
from selenium.webdriver.common.by import By

from settings.URLs import STAFF_ACCOUNT_BASE_URL
from utils.file_utils.staff_files import save_staff_as_json
from utils.web_utils.general_web import init_chrome_webdriver


def load_staff_webpage() -> webdriver:
    """
    Hämta första sidan.
    :param anvnamn:
    :return:
    """
    url = STAFF_ACCOUNT_BASE_URL + "search/users"
    driver = init_chrome_webdriver(headless_bool=False)
    driver.set_window_position(2560 + 10, -400)
    driver.set_window_size(1000, 1500)
    driver.get(url=url)
    return driver


def load_user_page(account_user_name: str) -> webdriver:
    """
    Hämta första sidan.
    :param account_user_name:
    :return:
    """
    driver = load_staff_webpage()
    driver.find_element(By.NAME, "Username").send_keys(account_user_name)  # fyll i användarnamnet
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    driver.find_element(By.LINK_TEXT, account_user_name).click()
    # account_user_name = extract_dt_info(driver, "Användarnamn")
    save_staff_as_json(account_user_name=extract_dt_info(driver, "Användarnamn"),
                       first_name=extract_dt_info(driver, "Förnamn"),
                       last_name=extract_dt_info(driver, "Efternamn"),
                       email=extract_dt_info(driver, "E-post"),
                       mobil=extract_dt_info(driver, "Mobil"),
                       telefon=extract_dt_info(driver, "Telefon"),
                       personnummer=extract_dt_info(driver, "Personnummer"),
                       slutdatum=extract_dt_info(driver, "Slutdatum"),
                       titel=extract_dt_info(driver, "Titel"),
                       )

    return


def extract_dt_info(driver: webdriver, element_name: str) -> webdriver:
    """    Hämta personnummer från anställningsinformationen. """
    for desc_list in driver.find_elements(By.CLASS_NAME, "dl-horizontal"):
        return desc_list.find_element(By.XPATH, f"./dt[.='{element_name}']/following-sibling::dd").text


if __name__ == "__main__":
    load_user_page(account_user_name="lyadol")

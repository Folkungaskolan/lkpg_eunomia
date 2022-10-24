import selenium
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from utils.creds import get_cred
from utils.file_utils import save_student_as_json
from utils.web_utils.general_web import init_chrome_webdriver


def import_student_from_web(account_user_name: str, headless_input_bool: bool = False) -> None:
    """ import a student from the web to a json file"""
    if account_user_name is None:
        raise ValueError("account_user_name is None")
    # TODO write import_student_from_web method
    driver = init_chrome_webdriver(headless_bool=headless_input_bool)
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


if __name__ == "__main__":
    pass

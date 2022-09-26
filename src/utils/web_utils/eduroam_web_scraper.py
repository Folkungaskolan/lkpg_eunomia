from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from CustomErrors import LogInFailure
from .general_web import init_firefox_webdriver


def get_single_student_user_from_web_to_json(account_user_name: str, verbose: str = False) -> None:
    if verbose:
        print(F"start {account_user_name=}")
    # TODO write get_single_student_user_from_web_to_json method


def generate_eduroam_for_user(account_user_name: str = None, google_pw: str = None, headless_input_bool: bool = True) -> str:
    """    Skapar eduroam användare    """
    print(F"start generate_and_save_eduroam_for_user for {account_user_name=} ")
    if account_user_name is None:
        raise ValueError("account_user_name is None")
    if google_pw is None:
        raise ValueError("google_pw is None")

    # initiera drivaren
    # behöver vara firefox för att kringgå problem med redan inloggad användare
    driver = init_firefox_webdriver(headless_bool=headless_input_bool)
    # Hämta sidan
    driver.get(url="https://itsupport.linkoping.se/form/eduroam")
    # Fyll i uppgifterna
    user_input = driver.find_element(By.NAME, "name")  # hitta vart användarnamnet ska in
    user_input.clear()  # töm rutan
    user_input.send_keys(account_user_name)  # fyll i användarnamnet
    pass_input = driver.find_element(By.NAME, "pswd")  # hitta vart lösenordet ska in
    pass_input.clear()  # töm rutan
    pass_input.send_keys(google_pw)  # fyll i lösenordet
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
        WebDriverWait(driver, 4 * 60).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "/html/body/div/div[2]/p[7]/span")))  # vänta på eduroam användaren
        eduroam_pass = driver.find_element(By.XPATH, "/html/body/div/div[2]/p[8]/span")  # hämta Lösen
        driver.close()  # Stäng fönstret
        return eduroam_pass.text


if __name__ == "__main__":
    pass

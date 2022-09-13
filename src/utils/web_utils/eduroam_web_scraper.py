from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

import Student
from CustomErrors import NoUserFoundError, LogInFailure
from general_web import init_firefox_webdriver


def get_single_user_from_web_to_json(account_user_name):
    pass


def generate_and_save_eduroam_for_user(account_user_name: str, headless_input_bool: bool = True) -> None:
    """    Skapar eduroam användare    """
    print(F"start {account_user_name=} ")
    # initiera drivaren
    try:
        user = Student.get_student_user_json_obj(account_user_name=account_user_name)
    except NoUserFoundError:
        get_single_user_from_web_to_json(account_user_name=account_user_name)
        user = Student.get_student_user_json_obj(account_user_name=account_user_name)
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
        Student.update_student_eduroam_password(account_user_name=account_user_name, new_eduroam_password=eduroam_pass.text)


if __name__ == "__main__":
    pass

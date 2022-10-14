""" Hanterar personal relaterade funktioner. Hämtar information om personal från webbplatsen >>> HTML """
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from sqlalchemy.orm import Session

from db.models import Staff_dbo
from db.mysql_db import init_db
from utils.decorators import function_timer
from utils.file_utils.staff_db import get_staff_user_from_db_based_on_user_id, update_staff_user
from utils.web_utils.general_web import init_chrome_webdriver


@function_timer
def update_single_staff_info_from_web_based_on_userid(user_id: str,
                                                      headless_input_bool: bool = False,
                                                      session: Session = None) -> Session:
    """ Hämtar personal information från webbplatsen """
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    user_id = user_id.lower().strip()

    driver = init_chrome_webdriver(headless_bool=headless_input_bool)
    kontohanterar_url = "https://kontohantering.linkoping.se/search/users"
    driver.set_window_position(2560, 0)
    driver.set_window_size(1000, 900)
    driver.get(url=kontohanterar_url)
    user_id_input = driver.find_element(By.NAME, "Username")  # hitta vart användarnamnet ska in
    user_id_input.send_keys(user_id)  # fyll i användarnamnet
    user_id_input.send_keys(Keys.RETURN)
    driver.find_element(By.LINK_TEXT, user_id).click()
    # Hämtar nu sidan med all information
    staff, session = get_staff_user_from_db_based_on_user_id(user_id=user_id, session=local_session)

    staff.pnr12 = driver.find_element(By.XPATH, "//dt[text()='Personnummer']/following-sibling::dd").text
    staff.first_name = driver.find_element(By.XPATH, "//dt[text()='Förnamn']/following-sibling::dd").text
    staff.last_name = driver.find_element(By.XPATH, "//dt[text()='Efternamn']/following-sibling::dd").text
    staff.full_name = driver.find_element(By.XPATH, "//dt[text()='Visningsnamn']/following-sibling::dd").text
    staff.titel = driver.find_element(By.XPATH, "//dt[text()='Titel']/following-sibling::dd").text
    staff.email = driver.find_element(By.XPATH, "//dt[text()='E-post']/following-sibling::dd").text
    staff.telefon = driver.find_element(By.XPATH, "//dt[text()='Telefon']/following-sibling::dd").text
    staff.u_created_date = driver.find_element(By.XPATH, "//dt[text()='Skapad']/following-sibling::dd").text
    staff.u_changed_date = driver.find_element(By.XPATH, "//dt[text()='Senast ändrad']/following-sibling::dd").text
    local_session.commit()
    if session is not None:
        return local_session


def update_staff_from_pnr12_list(pnr12_list: list) -> None:
    """ Uppdaterar personal från pnr12 listan """
    local_session = init_db()
    for pnr12 in pnr12_list:
        update_single_staff_info_from_web_based_on_userid(user_id=pnr12, session=local_session)


@function_timer
def update_single_staff_info_from_web_based_on_pnr12(pnr12: str,
                                                     headless_input_bool: bool = False,
                                                     session: Session = None) -> Session:
    """ Hämtar personal information från webbplatsen """
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    pnr12 = pnr12.lower().strip()

    driver = init_chrome_webdriver(headless_bool=headless_input_bool)
    kontohanterar_url = "https://kontohantering.linkoping.se/search/users"
    driver.set_window_position(2560, 0)
    driver.set_window_size(1000, 900)
    driver.get(url=kontohanterar_url)
    pnr_input = driver.find_element(By.NAME, "PersonNo")  # hitta vart användarnamnet ska in
    pnr_input.send_keys(pnr12)  # fyll i användarnamnet
    pnr_input.send_keys(Keys.RETURN)
    driver.find_element(By.LINK_TEXT, pnr12).click()
    # Hämtar nu sidan med all information
    staff = local_session.query(Staff_dbo).filter_by(pnr12=pnr12).first()
    if staff is None:
        staff = Staff_dbo()
    staff.user_id = driver.find_element(By.XPATH, "//dt[text()='Användarnamn']/following-sibling::dd").text
    staff.pnr12 = driver.find_element(By.XPATH, "//dt[text()='Personnummer']/following-sibling::dd").text
    staff.first_name = driver.find_element(By.XPATH, "//dt[text()='Förnamn']/following-sibling::dd").text
    staff.last_name = driver.find_element(By.XPATH, "//dt[text()='Efternamn']/following-sibling::dd").text
    staff.full_name = driver.find_element(By.XPATH, "//dt[text()='Visningsnamn']/following-sibling::dd").text
    staff.titel = driver.find_element(By.XPATH, "//dt[text()='Titel']/following-sibling::dd").text
    staff.email = driver.find_element(By.XPATH, "//dt[text()='E-post']/following-sibling::dd").text
    staff.telefon = driver.find_element(By.XPATH, "//dt[text()='Telefon']/following-sibling::dd").text
    staff.u_created_date = driver.find_element(By.XPATH, "//dt[text()='Skapad']/following-sibling::dd").text
    staff.u_changed_date = driver.find_element(By.XPATH, "//dt[text()='Senast ändrad']/following-sibling::dd").text
    local_session.add(staff)
    local_session.commit()
    if session is not None:
        return local_session


@function_timer
def update_all_staff_info_from_web(headless_input_bool: bool = False) -> None:
    """ Hämtar personal information från webbplatsen till databasen"""
    local_session = init_db()
    staff_list = local_session.query(Staff_dbo).filter(Staff_dbo.pnr12 == None).all()
    # print(staff_list.count())
    for staff in staff_list:
        print(F"Updating {staff.user_id}")
        try:
            local_session = update_single_staff_info_from_web_based_on_userid(user_id=staff.user_id,
                                                                              headless_input_bool=headless_input_bool,
                                                                              session=local_session)
        except NoSuchElementException as e:
            print(f"Kunde inte uppdatera {staff.user_id} från webbplatsen. {e}")
            local_session = update_staff_user(user_id=staff.user_id,
                                              email="error",
                                              domain="slutat?",
                                              pnr12="000000000000",
                                              session=local_session)
            continue


if __name__ == "__main__":
    # update_single_staff_info_from_web(user_id="lyadol", headless_input_bool=False)
    # update_all_staff_info_from_web(headless_input_bool=True)
    update_single_staff_info_from_web_based_on_pnr12(pnr12="199302243879", headless_input_bool=False)
    pass

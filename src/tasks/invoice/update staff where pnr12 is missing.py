"""
Task fil. Hämta från hemsida användare som saknar pnr12
"""
import threading

import numpy as np
from selenium.common import NoSuchElementException
from sqlalchemy.sql.elements import or_

from database.models import Staff_dbo
from database.mysql_db import init_db
from utils.web_utils.general_web import init_chrome_webdriver, position_windows
from utils.web_utils.staff_web_scraper import update_single_staff_info_from_web_based_on_userid


# update_single_staff_info_from_web_based_on_pnr12("19810101-0000")

def main(nr_of_threads: int, headless_bool=False) -> None:
    """ Vilka användare behöver hämtas från Web? """
    session = init_db()
    threads = []
    staff = session.query(Staff_dbo).filter(or_(Staff_dbo.pnr12 == None,
                                                Staff_dbo.email == "error",
                                                Staff_dbo.domain == "Slutat?")).all()
    sub_tasks = np.array_split(staff, nr_of_threads)
    for i, sub_task_list in enumerate(sub_tasks):
        print(len(sub_task_list), sub_task_list)
        thread = threading.Thread(target=process_sub_tasks, args=(sub_task_list, i, headless_bool))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def process_sub_tasks(task_list: list[str], thread_nr: int, headless_input_bool=False) -> None:
    """kör trådarna"""
    local_session = init_db()
    local_driver = init_chrome_webdriver(headless_bool=headless_input_bool)
    local_driver = position_windows(local_driver, position_nr=thread_nr)
    for task in task_list:
        print(f"Thread {thread_nr}: {task.user_id}")
        try:
            local_session, local_driver = update_single_staff_info_from_web_based_on_userid(user_id=task.user_id,
                                                                                            session=local_session,
                                                                                            driver=local_driver)
        except NoSuchElementException as e:
            staff = local_session.query(Staff_dbo).filter_by(user_id=task.user_id).first()
            print(f"Kunde inte uppdatera {staff.user_id} från webbplatsen.")
            staff.user_id = staff.user_id
            staff.email = "error"
            staff.domain = "slutat?"
            staff.pnr12 = "000000000000"
            local_session.commit()
            continue


if __name__ == "__main__":
    main(nr_of_threads=4)

"""
Task fil. Hämta från hemsida användare som saknar pnr12
"""
import threading

import numpy as np
from sqlalchemy.sql.elements import or_

from db.models import Staff_dbo
from db.mysql_db import init_db
from utils.web_utils.general_web import init_chrome_webdriver, SCREEN_POSITIONS
from utils.web_utils.staff_web_scraper import update_single_staff_info_from_web_based_on_userid


# update_single_staff_info_from_web_based_on_pnr12("19810101-0000")

def main():
    session = init_db()
    nr_of_threads = 4
    threads = []
    staff = session.query(Staff_dbo).filter(or_(Staff_dbo.pnr12 == None,
                                                Staff_dbo.email == "error",
                                                Staff_dbo.domain == "Slutat?")).all()
    sub_tasks = np.array_split(staff, nr_of_threads)
    for i, sub_task_list in enumerate(sub_tasks):
        print(len(sub_task_list), sub_task_list)
        thread = threading.Thread(target=process_sub_tasks, args=(sub_task_list, i, False))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def process_sub_tasks(task_list: list[str], thread_nr: int, headless_input_bool=False) -> None:
    """kör trådarna"""
    local_session = init_db()
    local_driver = init_chrome_webdriver(headless_bool=headless_input_bool)
    local_driver.set_window_position(SCREEN_POSITIONS[thread_nr]["x"], SCREEN_POSITIONS[thread_nr]["y"])
    local_driver.set_window_size(SCREEN_POSITIONS[thread_nr]["width"], SCREEN_POSITIONS[thread_nr]["height"])
    for task in task_list:
        print(f"Thread {thread_nr}: {task.user_id}")
        local_session, local_driver = update_single_staff_info_from_web_based_on_userid(user_id=task.user_id,
                                                                                        session=local_session,
                                                                                        driver=local_driver)


if __name__ == "__main__":
    main()

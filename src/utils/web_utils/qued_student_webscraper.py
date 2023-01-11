""" Celery version of student web scraper """
from __future__ import annotations

import multiprocessing
import queue
import threading
import time

import selenium
import sqlalchemy
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from database.mysql_db import MysqlDb, init_db
from settings.threadsettings import THREADCOUNT
from utils.file_utils.to_csv import write_student_csv_from_mysql
from utils.print_progress_bar import print_progress_bar
from utils.que_utils.my_queue import add_task_to_db_queue, increment_task_run_counter, mark_task_as_done, get_webid_tasks_from_db
from utils.student.student_mysql import save_student_information_to_db, count_student
from utils.web_utils.general_web import init_chrome_webdriver, position_windows
from utils.web_utils.student_web_scraper import login_student_accounts_page


def _1_scrape_web_ids_from_web_to_db(run_only_class: list[str] = None, force_single_thread: bool = False, headless_bool: bool = True) -> None:
    """ scrape web ids from web to db """
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
    url_queue = queue.Queue()
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
                url_queue.put(F'https://elevkonto.linkoping.se/users?FreeText=&School={url_skola}&SchoolClass={option.text}')
                url_queue.put(F'https://elevkonto.linkoping.se/users?FreeText=&School={url_skola}&SchoolClass={option.text}&_page=2')
            elif option.text in run_only_class:
                url_queue.put(F'https://elevkonto.linkoping.se/users?FreeText=&School={url_skola}&SchoolClass={option.text}')
                url_queue.put(F'https://elevkonto.linkoping.se/users?FreeText=&School={url_skola}&SchoolClass={option.text}&_page=2')
    print("listing urls finnished                                    2022-10-27 11:23:11")
    driver.close()
    print("url queue size : ")
    print(url_queue.qsize())
    if force_single_thread:
        t_fn_rips_web_ids_from_qued_urls(url_queue=url_queue, headless_bool=headless_bool)
    else:
        threads = []
        nr_of_threads = THREADCOUNT
        for i in range(1, nr_of_threads):
            t = threading.Thread(target=t_fn_rips_web_ids_from_qued_urls, args=(url_queue, headless_bool, i))
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()
    MysqlDb().session().commit()


def t_fn_rips_web_ids_from_qued_urls(url_queue: multiprocessing.queues, headless_bool: bool = True, thread_nr: int = 0) -> None:
    """ saves web ids to task que for students for processing into student records """
    driver = init_chrome_webdriver(headless_bool=headless_bool)
    driver = login_student_accounts_page(driver)
    # print(f"starting thread {thread_nr} with {url_queue.qsize()} queue size")
    if not headless_bool:
        position_windows(driver=driver, position_nr=(thread_nr % 4) + 1)
    if thread_nr == 1:
        l = url_queue.qsize()
        print_progress_bar(0, l, prefix='Progress:', suffix='Complete', length=50)
    while url_queue.empty() is False:
        url = url_queue.get()
        if thread_nr == 1:
            print_progress_bar(l - url_queue.qsize(), l, prefix='Progress:', suffix='Complete', length=50)
        driver.get(url=url)
        rows = driver.find_elements(by=By.CLASS_NAME, value="item-row")
        for row in rows:
            data_item_id = row.get_attribute("data-item-id")
            if data_item_id is not None:
                add_task_to_db_queue(process_function="web_id_for_student", kwargs=data_item_id)
    driver.close()
    print(F"web->webid Thread {thread_nr} done")


def _2_process_web_ids(force_single_thread: bool = False, headless_bool: bool = True) -> None:
    webid_queue = get_webid_tasks_from_db()

    if force_single_thread:
        t_fn_get_student_from_webid(webid_queue=webid_queue, headless_bool=headless_bool)
    else:
        threads = []
        if webid_queue.qsize() < 5:
            nr_of_threads = 1
        else:
            nr_of_threads = THREADCOUNT
        for i in range(1, nr_of_threads):
            t = threading.Thread(target=t_fn_get_student_from_webid, args=(webid_queue, headless_bool, i))
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()
    MysqlDb().session().commit()


def t_fn_get_student_from_webid(webid_queue: multiprocessing.queues, headless_bool: bool = True, thread_nr: int = 1) -> None:
    """ Converts webid to student records """
    driver = init_chrome_webdriver(headless_bool=headless_bool)
    driver = login_student_accounts_page(driver)
    s = init_db()
    if not headless_bool:
        position_windows(driver=driver, position_nr=(thread_nr % 4) + 1)
    if thread_nr == 1:
        start_count = webid_queue.qsize()
        print_progress_bar(0, start_count, prefix='Progress:', suffix='Complete', length=50)
    while webid_queue.empty() is False:
        left_count = webid_queue.qsize()
        item = webid_queue.get()
        row_id = item.id
        web_id = item.kwargs
        increment_task_run_counter(task_id=row_id, s=s)
        if thread_nr == 1:
            print_progress_bar(iteration=start_count - left_count,
                               total=start_count,
                               prefix='Progress:',
                               suffix=F'Complete {left_count} students left to process',
                               length=50)
        driver.get(url=F"https://elevkonto.linkoping.se/entity/view/user/{web_id}")
        google_pw = ""
        try:
            account_user_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[2]/div[2]/span").text
            birthday = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[1]/div[2]/span").text
            first_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[7]/div[2]/span").text
            last_name = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[8]/div[2]/span").text
            klass = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[13]/div[2]/span").text
            skola = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[10]/div[2]/span").text
            if klass == "ALV1214TEX04S":  # Av någon anledning får jag Anna Alkenius vuxen konto med i våra listor. Skippar den.
                mark_task_as_done(row_id)
                continue
        except selenium.common.exceptions.NoSuchElementException as e:
            print(f" process failed id:{web_id}")
            continue

        try:
            google_pw = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/article/div[2]/div/div[2]/div[1]/div[5]/div[2]/span").text
        except selenium.common.exceptions.NoSuchElementException as e:
            print(f" process failed id:{row_id} no pw found for user : {account_user_name}")
            continue
        else:
            save_student_information_to_db(user_id=account_user_name,
                                           first_name=first_name,
                                           last_name=last_name,
                                           klass=klass,
                                           skola=skola,
                                           birthday=birthday,
                                           google_pw=google_pw,
                                           session=s,
                                           webid=web_id
                                           )
            try:
                mark_task_as_done(task_id=row_id, s=s)
            except sqlalchemy.orm.exc.ObjectDeletedError:  # happens in the end when all threads are done and they take the last same row
                pass
            continue
    print(f"Done in thread {thread_nr}")

def fetch_all_students_from_web() -> None:
    """ Fetches all students from web """
    _1_scrape_web_ids_from_web_to_db()
    _2_process_web_ids()
    count_student()
    write_student_csv_from_mysql()

if __name__ == '__main__':
    # _1_scrape_web_ids_from_web_to_db(run_only_class="9A_FOL13")
    # _1_scrape_web_ids_from_web_to_db(force_single_thread=True,headless_bool=False)
    _2_process_web_ids()
    # count_student()
    # write_student_csv_from_mysql()

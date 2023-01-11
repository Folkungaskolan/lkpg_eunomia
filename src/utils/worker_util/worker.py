import queue
import time

from sqlalchemy import and_

from database.models import Eunomia_process_que_dbo
from database.mysql_db import MysqlDb
from utils.que_utils.my_queue import add_task_to_db_queue


def start_task_setter():
    """ Betar av alla tasks i kön """
    s = MysqlDb().session()
    print("starting_work_checker")
    i = 0
    limit = 3
    while i < limit:
        task_funktions = s.query(Eunomia_process_que_dbo).filter(Eunomia_process_que_dbo.completed == None).distinct().all()
        running_task_threads = []
        for task_group in task_funktions:
            group_tasks = s.query(Eunomia_process_que_dbo).filter(and_(Eunomia_process_que_dbo.completed == None,
                                                                       Eunomia_process_que_dbo.process_function == task_group)
                                                                  ).all()
            group_que = queue.Queue()
            for task in group_tasks:
                group_que.put(task)




        print("task setter sleeping")
        for j in range(1,3):
            print(f"task setter sleeping {j}")
            time.sleep(1)
        i +=  1
        print(f"while loop {i} < {limit}")


def set_gear_fasit_web_user_to(gear_id: str, user_id: str) -> None:
    """ set gear fasit web user to """
    print(gear_id, user_id)

def add_task(process_function,kwargs) -> None:
    """ add task to db que """
    s = MysqlDb().session()
    s.add(Eunomia_process_que_dbo(process_function=process_function, kwargs=kwargs))
    s.commit()


if __name__ == '__main__':
    add_task("set_gear_fasit_web_user_to", "{'gear_id': 'E52076', 'user_id': 'lyadol'}")
    start_task_setter()

import multiprocessing
import queue
from datetime import datetime

from sqlalchemy import and_, or_

from database.models import Eunomia_process_que_dbo
from database.mysql_db import MysqlDb
from utils.EunomiaEnums import TaskStatus


def add_task_to_db_queue(process_function: str, kwargs: str) -> None:
    """ add task to que """
    s = MysqlDb().session()
    s.add(Eunomia_process_que_dbo(process_function=process_function, kwargs=kwargs))


def increment_task_run_counter(task_id: int, s: MysqlDb) -> None:
    """ increment task run counter """
    task = s.query(Eunomia_process_que_dbo).filter(Eunomia_process_que_dbo.id == task_id).first()
    task.times_run += 1
    s.commit()


def mark_task_as_done(task_id: int, s: MysqlDb) -> None:
    """ mark task as done """
    task = s.query(Eunomia_process_que_dbo).filter(Eunomia_process_que_dbo.id == task_id).first()
    task.completed = datetime.now()
    task.status = TaskStatus.DONE.value
    s.commit()


def get_webid_tasks_from_db() -> multiprocessing.Queue:
    """ get all ids from db and load them to the que """
    task_queue = queue.Queue()
    s = MysqlDb().session()
    web_ids = s.query(Eunomia_process_que_dbo
                      ).filter(and_(or_(Eunomia_process_que_dbo.status == TaskStatus.IN_PROGRESS.value,
                                        Eunomia_process_que_dbo.status == TaskStatus.NEW.value
                                        ), Eunomia_process_que_dbo.completed == None
                                    ), Eunomia_process_que_dbo.process_function == "web_id_for_student"
                               ).all()
    for item in web_ids:
        # print(item.process_function, item.kwargs)
        task_queue.put(item)
    return task_queue

if __name__ == '__main__':
    increment_task_run_counter(1)
    mark_task_as_done(1)

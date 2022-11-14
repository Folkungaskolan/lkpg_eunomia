""" Funktioner för decorators """
from datetime import datetime
from time import time, sleep

from database.models import RunTime_dbo
from database.mysql_db import MysqlDb


def function_timer(func):
    """ tar tid hur länge det tar att köra viss funktion."""

    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        """ wrapper function """
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        run_time = t2 - t1
        print(f'Function {func.__name__!r}  with arg:{args} and kw:{kwargs}  executed in {(run_time):.4f}s')
        for k in kwargs:
            if type(kwargs[k]) == list:
                write_runtime_to_db(func_name=func.__name__, list_length=len(kwargs[k]), run_time_sec=t2 - t1)
        return result

    return wrap_func


def write_runtime_to_db(func_name: str, list_length: int, run_time_sec: float) -> None:
    """ Skriver körtid till db """
    s = MysqlDb().session()
    print(f'Function {func_name!r}  with list length:{list_length}  executed in {(run_time_sec):.4f}s')
    s.add(RunTime_dbo(run_date=datetime.now(),
                      function_name=func_name,
                      list_length=list_length,
                      run_time_sec=run_time_sec,
                      avg_time_sec=run_time_sec / list_length)
          )
    s.commit()


@function_timer
def demo_function_timer(l: list) -> None:
    """ demo av function_timer """
    for i in l:
        sleep(0.1)
        print(i)


if __name__ == "__main__":
    demo_function_timer(l=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

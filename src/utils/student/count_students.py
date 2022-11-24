""" hanterar funktioner som gör något mot för studenter"""
import math
from datetime import datetime
from functools import cache

from sqlalchemy import func, and_


from database.models import Student_dbo, StudentCount_dbo
from database.mysql_db import init_db, MysqlDb
from settings.enhetsinfo import ID_AKTIVITET, FOLKUNGA_GY_ENHETER, FOLKUNGA_GRU_ENHETER, ENHETER_SOM_HAR_CBS, STLARS_ENHETER
from utils.decorators import function_timer




if __name__ == "__main__":
    # split = generate_split_on_student_count(year=2022, month=11, enheter_to_split_over={"CB"})
    # print(split)
    pass
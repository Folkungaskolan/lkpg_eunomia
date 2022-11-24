""" hjälp funktoiner för fasit copy tabellen"""
from functools import cache

from database.models import FasitCopy
from database.mysql_db import MysqlDb


def get_fasit_row(name: str) -> FasitCopy:
    """ Hämta fasit rad från databasen"""
    s = MysqlDb().session()
    return s.query(FasitCopy).filter(FasitCopy.name == name).first()


if __name__ == '__main__':
    pass

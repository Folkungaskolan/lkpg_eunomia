from database.models import FakturaRad_dbo
from database.mysql_db import MysqlDb


def a(row):
    row.avser = "p"

if __name__ == '__main__':
    s = MysqlDb().session()
    rows = s.query(FakturaRad_dbo).limit(5).all()
    for row in rows:
        print(row.avser)
        a(row)
        print(row.avser)
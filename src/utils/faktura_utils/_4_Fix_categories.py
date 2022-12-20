""" """
from database.models import FakturaRadSplit_dbo
from database.mysql_db import MysqlDb


def fix_categories() -> None:
    """ Fixa kategorierna för fakturans tjänster """
    # s = MysqlDb().session()
    # alla_rader = s.query(FakturaRadSplit_dbo).all()
    pass


if __name__ == "__main__":
    fix_categories()

""" Hämta data från databasen och uppdater FASIT / CBA"""
from database.models import FasitCopy
from database.mysql_db import MysqlDb
from utils.dbutil.fasit_db import get_needed_web_updates


def update_cba_from_db() -> None:
    """ update CB """
    updates = get_needed_web_updates()
    # TODO skriv web uppdaterare
    # s.commit()

if __name__ == "__main__":
    update_cba_from_db()

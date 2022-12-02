""" expandera enheter för id_komplement_pa """
from database.mysql_db import MysqlDb
from settings.enhetsinfo import ID_AKTIVITET


def expandera_enheter(enheter_att_expandera: list[str]) -> list[str]:
    """ Expandera enheter för id_komplement_pa """
    s = MysqlDb().session()
    expandrade_enheter = []
    alla_enheter = set(ID_AKTIVITET.keys())
    for enhet in alla_enheter:
        for e in enheter_att_expandera:
            if enhet.startswith(e):
                expandrade_enheter.append(enhet)
    return expandrade_enheter


if __name__ == '__main__':
    print(expandera_enheter(["655", "656"]))
    print(expandera_enheter(["655"]))

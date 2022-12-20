""" hjälp för att nollställa en rad i en databas """
from database.models import FakturaRad_dbo, FakturaRadSplit_dbo
from database.mysql_db import MysqlDb


def reset_avser(avser) -> None:
    """ Nollställ alla rader med av avser """
    s = MysqlDb().session()
    faktura_rader = s.query(FakturaRad_dbo).filter(FakturaRad_dbo.avser == avser).all()
    for rad in faktura_rader:
        rad.split_done = False
        split_rader = s.query(FakturaRadSplit_dbo).filter(FakturaRadSplit_dbo.split_id == rad.id).all()
        for split_rad in split_rader:
            s.delete(split_rad)
    s.commit()


def reset_faktura_row_id(row_ids: int) -> None:
    """ Nollställer delning för rad med id"""
    s = MysqlDb().session()
    for id in row_ids:
        faktura_rad = s.query(FakturaRad_dbo).filter(FakturaRad_dbo.id == id).first()
        faktura_rad.split_done = False
        split_rader = s.query(FakturaRadSplit_dbo).filter(FakturaRadSplit_dbo.split_id == id).all()
        for split_rad in split_rader:
            s.delete(split_rad)
    s.commit()


if __name__ == '__main__':
    # reset_avser("E37571")
    reset_faktura_row_id(12706)
    pass

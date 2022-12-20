""" Separera ärenden i faktura raderna för att få ut kostnaden för Chromebook reparationerna """
from CustomErrors import NoUserFoundError
from database.models import FakturaRad_dbo
from database.mysql_db import MysqlDb
from utils.dbutil.fasit_db import get_user_id_for_fasit_user
from utils.file_utils.to_csv import write_case_costs_to_csv

from utils.strips_parentheses import strips_parentheses


def separera_cb_repair_cases():
    """ Separera ärenden i faktura raderna för att få ut kostnaden för Chromebook reparationerna """
    s = MysqlDb().session()
    search = F"%ärende%"
    case_faktura_rader = s.query(FakturaRad_dbo).filter(FakturaRad_dbo.tjanst.like(search)).all()
    for faktura_rad in case_faktura_rader:
        case_id = faktura_rad.tjanst.split(" ")
        faktura_rad.eunomia_case_id = case_id[1]
        user_id = get_user_id_for_fasit_user(strips_parentheses(faktura_rad.tjanst.split("(")[1]))
        # print(F"{faktura_rad.tjanst:}|{user_id}")
        faktura_rad.eunomia_case_creator_user_id = user_id
    s.commit()
    write_case_costs_to_csv()


if __name__ == '__main__':
    separera_cb_repair_cases()

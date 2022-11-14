from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Staff_dbo
from database.mysql_db import  MysqlDb
from settings.folders import STAFF_USER_FOLDER_PATH
from utils.creds import get_cred
from utils.file_utils.json_wrapper import load_dict_from_json_path


def move_staff_json_to_db_one_write(echo: bool = False):
    """
    Move staff json to database.
    one write on the sql side
    """
    s =  MysqlDb().session()
    filelist = list(Path(STAFF_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
    for file in filelist:
        # if "niksor" not in str(file):
        #     continue
        print(file)
        created_locally = False
        staff_user = load_dict_from_json_path(filepath=file)
        if 'personnummer' in staff_user.keys():
            staff = s.query(Staff_dbo).filter(Staff_dbo.pnr12 == staff_user['personnummer']).first()
        else:
            if staff is None:  # hittades inte på pnr
                staff = s.query(Staff_dbo).filter(
                    Staff_dbo.user_id == staff_user['account_1_user_name']).first()

        if staff is None:  # hittades inte på user_id
            staff = Staff_dbo(user_id=staff_user['account_1_user_name'],
                              pnr12=staff_user['personnummer'])
            created_locally = True
        staff.user_id = staff_user['account_1_user_name']
        if 'account_2_first_name' in staff_user.keys():
            staff.first_name = staff_user['account_2_first_name']
        if 'account_2_last_name' in staff_user.keys():
            staff.last_name = staff_user['account_2_last_name']
        if 'domain' in set(staff_user.keys()):
            staff.domain = staff_user['domain']
        if 'account_3_email' in staff_user.keys():
            staff.email = staff_user['account_3_email']
        if 'telefon' in staff_user.keys():
            staff.telefon = staff_user['telefon']
        if 'titel' in staff_user.keys():
            staff.titel = staff_user['titel']
        if created_locally:
            s.add(staff)
            s.commit()
        else:
            s.commit()


if __name__ == '__main__':
    # reset_mysql_db()
    move_staff_json_to_db_one_write(echo=False)

    # reset_mysql_db()
    # move_staff_json_to_db_one_write_pnr(echo=False)

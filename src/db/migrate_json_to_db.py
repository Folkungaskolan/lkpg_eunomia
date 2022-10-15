from pathlib import Path

from
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Staff_dbo
from db.mysql_db import init_db
from settings.folders import STAFF_USER_FOLDER_PATH
from utils.creds import get_cred
from utils.decorators import function_timer
from utils.file_utils.json_wrapper import load_dict_from_json_path

creds = get_cred(account_file_name="mysql_root_local")
engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/eunomia", echo=True)
Session = sessionmaker(bind=engine)
session = Session()


# @timer_func
# def move_staff_json_to_db_1by1(echo: bool = False):
#     """ Move staff json to db. one at a time on the sql side """
#     local_session = init_db(echo=echo)
#     filelist = list(Path(STAFF_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
#     for file in filelist:
#         staff_user = load_dict_from_json_path(filepath=file)
#         local_session = update_user(user_id=staff_user['account_user_name'],
#                                     first_name=staff_user['first_name'],
#                                     last_name=staff_user['last_name'],
#                                     domain=staff_user['domain'],
#                                     email=staff_user['email'],
#                                     session=local_session)

@function_timer
def move_staff_json_to_db_one_write(echo: bool = False):
    """
    Move staff json to db.
    one write on the sql side
    """
    local_session = init_db(echo=echo)
    filelist = list(Path(STAFF_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
    for file in filelist:
        staff_user = load_dict_from_json_path(filepath=file)
        staff = Staff_dbo(user_id=staff_user['account_user_name'])
        if 'first_name' in staff_user.keys():
            staff.first_name = staff_user['first_name']
        if 'last_name' in staff_user.keys():
            staff.last_name = staff_user['last_name']
        if 'domain' in set(staff_user.keys()):
            staff.domain = staff_user['domain']
        if 'email' in staff_user.keys():
            staff.email = staff_user['email']
        if 'pnr' in staff_user.keys():
            staff.pnr = staff_user['pnr']
        local_session.add(staff)
    local_session.commit()


if __name__ == '__main__':
    # reset_mysql_db()
    # move_staff_json_to_db_1by1(echo=False)

    # reset_mysql_db()
    move_staff_json_to_db_one_write(echo=False)

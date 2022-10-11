from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.mysql_db import init_db
from settings.folders import STAFF_USER_FOLDER_PATH
from utils.creds import get_cred
from utils.file_utils.json_wrapper import load_dict_from_json_path
from utils.file_utils.staff_db import update_user

creds = get_cred(account_file_name="mysql_root_local")
engine = create_engine(f"mysql+mysqldb://{creds['usr']}:{creds['pw']}@localhost/eunomia", echo=True)
Session = sessionmaker(bind=engine)
session = Session()


def move_staff_json_to_db():
    """ Move staff json to db. """
    local_session = init_db()
    filelist = list(Path(STAFF_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
    for file in filelist:
        staff_user = load_dict_from_json_path(filepath=file)
        local_session = update_user(user_id=staff_user['account_user_name'],
                                    first_name=staff_user['first_name'],
                                    last_name=staff_user['last_name'],
                                    domain=staff_user['domain'],
                                    email=staff_user['email'],
                                    session=local_session)


if __name__ == '__main__':
    move_staff_json_to_db()

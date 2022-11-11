""" lyft upp json eduroam uppgifterna från Json till databasen"""
from pathlib import Path

from database.models import Student_dbo
from database.mysql_db import init_db
from settings.folders import STUDENT_USER_FOLDER_PATH
from utils.file_utils.json_wrapper import load_dict_from_json_path


def lift_json_to_db():
    """ lyft upp json eduroam uppgifterna från Json till databasen"""
    filelist = list(Path(STUDENT_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
    print(F"len {len(filelist)}:filelist")
    local_session = init_db()
    for filepath in filelist:
        user = load_dict_from_json_path(filepath=filepath)
        print(user)
        user_id = user["account_1_user_name"]
        student = local_session.query(Student_dbo).filter(Student_dbo.user_id == user_id).first()
        if student.eduroam_pw is None and user.get("account_3_eduroam_pw", None) is not None:
            student.eduroam_pw = user["account_3_eduroam_pw"]
            student.eduroam_pw_gen_date = user["account_3_eduroam_pw_gen_date"]
    local_session.commit()


if __name__ == '__main__':
    lift_json_to_db()

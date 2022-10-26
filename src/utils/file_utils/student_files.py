""" student relaterade funktioner """
from datetime import datetime
from pathlib import Path

from CustomErrors import NoUserFoundError
from database.models import Student_dbo
from database.mysql_db import init_db
from settings.folders import STUDENT_USER_FOLDER_PATH


def find_student_json_filepath(account_user_name: str, verbose: bool = False) -> str:
    """
    :param account_user_name: str användarens användarnamn
    :param verbose: bool  skriv ut mer info i terminalen
    :return: str  sökväg till json filen som sträng
    """
    try:
        filelist = list(Path(STUDENT_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
        if verbose:
            print(F"filelist len = {len(filelist)}                                 2022-09-16 09:04:47")
        for i, filepath in enumerate(filelist):
            if verbose:
                print(F"{i}:{filepath}")
            if account_user_name in str(filepath.stem):
                if verbose:
                    print(F"hittad : {filepath}                                     2022-09-16 09:04:54")
                return str(filepath)
    except Exception as e:
        print(e)
        if verbose:
            print("2022-09-16 09:04:00")
            print(account_user_name)
            print(filepath)
        raise
    raise NoUserFoundError(F"User Json  for {account_user_name} not found")


def save_student(user_id: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 klass: str = None,
                 skola: str = None,
                 birthday: str = None,
                 google_pw: str = None,
                 eduroam_pw: str = None,
                 eduroam_pw_gen_datetime: datetime = None,
                 webid: str = None,
                 this_is_a_web_import: bool = False
                 ) -> None:
    """ Sparar ny information, tar inte bort gamla värden
    :param user_id: användarens användarnamn
    :param first_name: förnamn för användaren
    :param last_name: efternamn för användaren
    :param klass: klass för användaren
    :param skola: skola för användaren
    :param birthday: födelsedag användaren
    :param google_pw: google lösenord användaren
    :param eduroam_pw: eduroam lösenord användaren
    :param eduroam_pw_gen_datetime: när genererades detta eduroam lösenord
    :param do_not_retain_old_info:
    :param this_is_a_web_import:

    :type this_is_a_web_import:
    :type do_not_retain_old_info: bool
    :return: funktionen skriver en fil till disk. Inget returneras.
    """
    if user_id is None:
        raise ValueError("account_user_name is None")
    session = init_db()
    student = session.query(Student_dbo).filter(Student_dbo.user_id == user_id).first()
    if student is None:
        student = Student_dbo(user_id=user_id)
        session.add(student)
        session.commit()

    if klass is None:
        student.klass = "undetermined_class"
    else:
        student.klass = klass

    if this_is_a_web_import:
        student.last_web_import = datetime.now()
    if first_name is not None:
        student.first_name = first_name
    if last_name is not None:
        student.last_name = last_name
    if skola is not None:
        student.skola = skola
    if birthday is not None:
        student.birthday = birthday
    if google_pw is not None:
        student.google_pw = google_pw
    if eduroam_pw is not None:
        student.eduroam_pw = eduroam_pw
        if student.eduroam_pw_gen_datetime is None:
            student.eduroam_pw_gen_datetime = datetime.now()
        else:
            student.eduroam_pw_gen_datetime = eduroam_pw_gen_datetime
    if webid is not None:
        student.webid = webid
    session.commit()


if __name__ == '__main__':
    save_student(user_id="test1", first_name="test åäö", last_name="test3", klass="test4", skola="test5", birthday="2022-01-01", google_pw="test7")
    pass

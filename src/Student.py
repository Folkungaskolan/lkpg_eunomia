import datetime
from pathlib import Path

from CustomErrors import NoUserFoundError
from Person import Person
from settings.folders import STUDENT_USER_FOLDER_PATH
from utils import load_dict_from_json_path
from utils.file_utils.excel import write_student_xlsx_from_json


class Student(Person):
    """
    Elev Class som ska hantera allt man gör med en Elev
    arbetar normalt mot json filer i specifik mapp STUDENT_USER_FOLDER_PATH
    hämtar endast från web om elev inte finns alls i mapp, annars antar den att informationen är korrekt.
    om den inte får indikation på motsatsen.
    Möjliga Actions:
    -import från web
        -när eleven inte finns som json fil
        -när elevens lösenord inte fungerar på eduroam
        -när klass börjar vis all update
    -byta eduroam lösenord
    -byta google lösenord
    -hämta all info på web till json filerna och uppdatera dessa
    -skapa excel filer
    -skapa csv filer
    -skapa pdf filer
        - användar uppgifter för terministart
            Innehåller :
            - användarnamn
            - google lösenord
            - eduroam lösenord
            - klass
        - klasslistor för retur av Chromebooks
        - klasslistor för return av Nycklar

    """

    def __init__(self, account_user_name: str = None, verbose: bool = False, auto_fetch_from_web: bool = False):
        if account_user_name is None:
            raise ValueError("account_user_name must be given")
        else:
            self.account_user_name: str = account_user_name
        self._email: str = F"{account_user_name}@edu.linkoping.se"
        self._klass: str = None
        self._google_pw: str = None
        self._eduroam_pw: str = None
        self._eduroam_pw_gen_datetime: datetime = None

        self._json_folder_path: str = STUDENT_USER_FOLDER_PATH
        self._user_json_path = None

        try:
            self.find_student_filepath(account_user_name=self.account_user_name)  # set self._user_json_path
        except (FileNotFoundError, NoUserFoundError) as e:
            print("                                                                               2022-09-16 09:05:27")
            # print(e)
            # self._user_json_path = None
            # if auto_fetch_from_web:
            #     self.get_user_from_web()
            # else:
            #     respons = input(f"User:{self.account_user_name} not found in {self._json_folder_path} do you wish to try web fetch? (y/n)")
            #     print(respons)
            #     print("                                                                               2022-09-16 09:05:34")
            #     raise NoUserFoundError("User Json not found")

        super().__init__(account_user_name=account_user_name, verbose=verbose)
        try:
            self.json_user_obj = load_dict_from_json_path(filepath=self._user_json_path)
        except Exception as e:
            print("                                                                               2022-09-16 09:05:41")
            print(e)
        else:
            self.unpack_user_json_obj()

    def find_student_filepath(self, account_user_name: str) -> None:
        try:
            filelist = list(Path(STUDENT_USER_FOLDER_PATH).rglob('*.[Jj][Ss][Oo][Nn]'))
            print(F"filelist len = {len(filelist)}                                 2022-09-16 09:04:47")
            for i, filepath in enumerate(filelist):
                print(F"{i}:{filepath}")
                if account_user_name in str(filepath.stem):
                    print(F"hittad : {filepath}                                     2022-09-16 09:04:54")
                self._user_json_path = str(filepath)
        except Exception as e:
            print(e)
            print("2022-09-16 09:04:00")
            print(account_user_name)
            print(filepath)
            raise
        raise NoUserFoundError(F"User Json  for {self.account_user_name} not found")

    def print_eduroam_pw(self) -> None:
        """ print the eduroam pw """
        print(F"eduroam_pw: {self._eduroam_pw}                                       2022-09-16 09:05:10")

    def gen_excel_files(self):
        """ generate excel files """
        if self.verbose:
            print(F"gen excel files for {self.account_user_name}                      2022-09-16 09:05:17")
        write_student_xlsx_from_json()  # utils.file_utils.excel.write_student_xlsx_from_json

    def gen_eduroam_pw(self) -> str:
        """ generate a new eduroam pw """
        if self.verbose:
            print(F"gen eduroam pw for {self.account_user_name}                      2022-09-16 09:05:24")
        # TODO write gen_eduroam_pw method
        return self._eduroam_pw

    @staticmethod
    def get_json_filepath() -> str:
        """ return the json filepath """
        print("                                                                              2022-09-16 09:05:31")
        return STUDENT_USER_FOLDER_PATH

    def get_account_user_name(self) -> str:
        if self.verbose:
            print(F"get account user name for {self.account_user_name}                     2022-09-16 09:08:00")
        return self.account_user_name

    def get_google_pw(self) -> str:
        """ get the google pw """
        if self.verbose:
            print(F"get google pw for {self.account_user_name}                             2022-09-16 09:08:10")
            print(F"get google pw for {self._google_pw}                                     2022-09-16 09:08:15")
        return self._google_pw

    def unpack_user_json_obj(self) -> None:
        """ unpack the user obj """
        if self.verbose:
            print(F"unpack user obj for {self.account_user_name}                             2022-09-16 09:08:22")
        try:
            self.first_name = self.json_user_obj['account_2_first_name']
        except KeyError as e:
            print(e)

        try:
            self.last_name = self.json_user_obj['account_2_last_name']
        except KeyError as e:
            print(e)

        try:
            self._google_pw = self.json_user_obj['google_pw']
        except KeyError as e:
            print(e)

        try:
            self._eduroam_pw = self.json_user_obj['eduroam_pw']
        except KeyError as e:
            print(e)

        try:
            self._eduroam_pw_gen_datetime: datetime = self.json_user_obj['account_3_eduroam_pw_gen_date']
        except KeyError as e:
            print(e)

        try:
            self._klass = self.json_user_obj['klass']
        except KeyError as e:
            print(e)

        try:
            self.name = self.json_user_obj['name']
        except KeyError as e:
            print(e)

        try:
            self._email = self.json_user_obj['email']
        except KeyError as e:
            print(e)

    def set_eduroam_pw(self, eduroam_pw: str) -> None:
        """ set the eduroam pw """
        self._eduroam_pw = eduroam_pw
        self.save()

    def save(self):
        """ save the student """
        # TODO write save method
        if self.verbose:
            print(F"save student {self.account_user_name}                                      2022-09-16 09:05:27")
        # TODO kolla att vi inte sparar 2 filer
        # TODO kolla ATT vi skriver över ett google_pw
        # TODO kolla att vi INTE skriver över ett eduroam_pw

    @classmethod
    def get_student_user_json_obj(cls, account_user_name: str) -> dict[str, str]:
        """ get a json obj based on a user account name """
        json_path = find_student_filepath(account_user_name=account_user_name)
        user = load_dict_from_json_path(filepath=json_path)
        return user

    @classmethod
    def update_student_eduroam_password(cls, account_user_name, new_eduroam_password) -> None:
        """ update the student eduroam password """
        pass  # TODO write update_student_eduroam_password

    def get_user_from_web(self):
        """
        get the user from the web
        """
        # TODO write get_user_from_web method
        pass


if __name__ == "__main__":
    # s = Student(account_user_name="knudat421")
    s = Student(account_user_name="abcdef123")

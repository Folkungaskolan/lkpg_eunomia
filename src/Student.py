import datetime

from CustomErrors import NoUserFoundError
from Person import Person
from settings.folders import STUDENT_USER_FOLDER_PATH
from utils import import_student_from_web
from utils import load_dict_from_json_path, generate_eduroam_for_user
from utils.file_utils.excel import write_student_csv_from_mysql
from utils.file_utils.student_files import save_student, find_student_json_filepath


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

    def __init__(self, account_user_name: str = None,
                 verbose: bool = False,
                 auto_fetch_from_web: bool = False,
                 first_name: str = None,
                 last_name: str = None,
                 google_pw: str = None,
                 klass: str = None,
                 skola: str = "Folkungaskolan",
                 birthday: str = None) -> None:
        if account_user_name is None:
            raise ValueError("account_user_name must be given")
        else:
            self.account_user_name: str = account_user_name
        self.verbose: bool = verbose
        self.auto_fetch_from_web = auto_fetch_from_web

        self._email: str = F"{account_user_name}@edu.linkoping.se"
        self._klass: str = klass
        self._google_pw: str = google_pw
        self._eduroam_pw: str = google_pw
        self._eduroam_pw_gen_datetime: datetime = None
        self._skola: str = skola

        self._first_name = first_name
        self._last_name = last_name
        self._birthday = birthday
        self._user_json_path = None

        self._json_folder_path: str = STUDENT_USER_FOLDER_PATH
        if self._first_name is None:  ## indikator om hela användaren är tom
            try:
                self._user_json_path = find_student_json_filepath(account_user_name=self.account_user_name)  # set self._user_json_path
            except (FileNotFoundError, NoUserFoundError) as e:
                print("   FileNotFoundError, NoUserFoundError                                             2022-09-16 09:05:27")
                self._user_json_path = None
                if auto_fetch_from_web:
                    self.get_user_from_web()
                else:
                    respons = input(f"User:{self.account_user_name} not found in {self._json_folder_path} do you wish to try web fetch? (y/n)")
                    print(F"respons: {respons}                                                    2022-09-26 14:44:36")
                    if respons == "y":
                        print(F"respons: {respons}                                                    2022-09-26 14:44:36")
                        self.get_user_from_web()
                    else:
                        print("                                                                               2022-09-26 14:44:14")
                        raise NoUserFoundError("User Json not found")
            try:
                self.json_user_obj = load_dict_from_json_path(filepath=self._user_json_path)
            except Exception as e:
                print("                                                                               2022-09-16 09:05:41")
                print(e)
            else:
                self.unpack_user_json_obj()
        super().__init__(account_user_name=account_user_name, verbose=verbose)


    def print_eduroam_pw(self) -> None:
        """ print the eduroam pw """
        print(F"eduroam_pw: {self._eduroam_pw}                                       2022-09-16 09:05:10")

    def gen_excel_files(self):
        """ generate excel files """
        if self.verbose:
            print(F"gen excel files for {self.account_user_name}                      2022-09-16 09:05:17")
        write_student_csv_from_mysql()  # utils.file_utils.excel.write_student_xlsx_from_json

    def gen_eduroam_pw(self) -> None:
        """ generate a new eduroam pw """
        if self.verbose:
            print(F"gen eduroam pw for {self.account_user_name}                      2022-09-16 09:05:24")
        self._eduroam_pw = generate_eduroam_for_user(account_user_name=self.account_user_name, verbose=self.verbose)
        self._eduroam_pw_gen_datetime = datetime.now()
        self.save()

    @staticmethod
    def get_json_filepath() -> str:
        """ return the json filepath """
        print("                                                                              2022-09-16 09:05:31")
        return STUDENT_USER_FOLDER_PATH

    def get_account_user_name(self) -> str:
        """
        return the account_user_name
        :return:
        """
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
            self._first_name = self.json_user_obj['account_2_first_name']
        except KeyError as e:
            print(e)

        try:
            self._last_name = self.json_user_obj['account_2_last_name']
        except KeyError as e:
            print(e)

        try:
            self._google_pw = self.json_user_obj['account_3_google_pw']
        except KeyError as e:
            print(e)

        try:
            self._eduroam_pw = self.json_user_obj['account_3_eduroam_pw']
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
            self._email = self.json_user_obj['email']
        except KeyError as e:
            self._email = self.account_user_name + "@edu.linkoping.se"
        pass

    def set_eduroam_pw(self, eduroam_pw: str) -> None:
        """ set the eduroam pw """
        self._eduroam_pw = eduroam_pw
        self.save()

    def save(self):
        """ save the student """
        if self.verbose:
            print(F"save student {self.account_user_name}                                      2022-09-16 09:05:27")
        save_student(user_id=self.account_user_name, first_name=self._first_name, last_name=self._last_name, klass=self._klass, google_pw=self._google_pw,
                     eduroam_pw=self._eduroam_pw, eduroam_pw_gen_datetime=self._eduroam_pw_gen_datetime)

    @classmethod
    def get_student_user_json_obj(cls, account_user_name: str) -> dict[str, str]:
        """ get a json obj based on a user account name """
        json_path = find_student_json_filepath(account_user_name=account_user_name)
        user = load_dict_from_json_path(filepath=json_path)
        return user

    @classmethod
    def update_student_eduroam_password(cls, account_user_name: str, new_eduroam_password: str) -> None:
        """ update the student eduroam password """
        # TODO write update_student_eduroam_password
        print(F"update student eduroam password for {account_user_name}                      2022-09-26 15:16:49")
        print(F"update student eduroam password for {new_eduroam_password}                   2022-09-26 15:16:43")

    def get_user_from_web(self):
        """ get the user from the web       """
        if self.verbose:
            print(F"get user from web for {self.account_user_name}                           2022-09-26 14:12:59")
            import_student_from_web(account_user_name=self.account_user_name)

    def __str__(self):
        return F"{self.account_user_name} {self._first_name} {self._last_name} {self._klass} {self._email} {self._google_pw} {self._eduroam_pw}"

    def print(self):
        """
        print the students class variables
        """
        instance_variables = vars(self)
        for key in instance_variables.keys():
            print(F"{key}:{instance_variables[key]}")


if __name__ == "__main__":
    # s = Student(account_user_name="knudat421")
    s = Student(account_user_name="abcdef123", verbose=True)
    print(s)

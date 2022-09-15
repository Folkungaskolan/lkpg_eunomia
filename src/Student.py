import datetime

import Person
from settings.folders import STUDENT_USER_FOLDER_PATH
from utils import find_student_filepath
from utils import load_dict_from_json_path


class Student(Person):
    def __init__(self, account_user_name: str = None, verbose: bool = False):
        if account_user_name is None:
            raise ValueError("account_user_name must be given")

        self.email = None
        self.name = None
        self.klass = None
        self.eduroam_pw = None
        self.google_pw = None

        self.json_folder_path = STUDENT_USER_FOLDER_PATH
        self.user_json_path = self.json_folder_path + account_user_name + '.json'

        super().__init__(account_user_name=account_user_name, verbose=verbose)
        try:
            self.json_user_obj = load_dict_from_json_path(filepath=self.user_json_path)
        except Exception as e:
            print(e)
        else:
            self.unpack_user_json_obj()

    @staticmethod
    def get_json_filepath() -> str:
        """ return the json filepath """
        return STUDENT_USER_FOLDER_PATH

    def get_account_user_name(self) -> str:
        if self.verbose:
            print(F"get account user name for {self.account_user_name}")
        return self.account_user_name

    def get_google_pw(self) -> str:
        """ get the google pw """
        if self.verbose:
            print(F"get google pw for {self.account_user_name}")
            print(F"get google pw for {self.google_pw}")
        return self.google_pw

    def unpack_user_json_obj(self) -> None:
        """ unpack the user obj """
        if self.verbose:
            print(F"unpack user obj for {self.account_user_name}")
        try:
            self.first_name = self.json_user_obj['account_2_first_name']
        except KeyError as e:
            print(e)

        try:
            self.last_name = self.json_user_obj['account_2_last_name']
        except KeyError as e:
            print(e)

        try:
            self.google_pw = self.json_user_obj['google_pw']
        except KeyError as e:
            print(e)

        try:
            self.eduroam_pw = self.json_user_obj['eduroam_pw']
        except KeyError as e:
            print(e)

        try:
            self.eduroam_pw_gen_datetime: datetime = self.json_user_obj['account_3_eduroam_pw_gen_date']
        except KeyError as e:
            print(e)

        try:
            self.klass = self.json_user_obj['klass']
        except KeyError as e:
            print(e)

        try:
            self.name = self.json_user_obj['name']
        except KeyError as e:
            print(e)

        try:
            self.email = self.json_user_obj['email']
        except KeyError as e:
            print(e)

    def set_eduroam_pw(self, eduroam_pw: str) -> None:
        """ set the eduroam pw """
        self.eduroam_pw = eduroam_pw
        self.save()

    def save(self):
        """ save the student """
        # TODO write save method
        if self.verbose:
            print(F"save student {self.account_user_name}")

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


if __name__ == "__main__":
    s = Student()

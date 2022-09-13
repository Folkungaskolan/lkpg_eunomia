import Person
from utils import
from utils import load_dict_from_json_path


class Student(Person):
    def __init__(self, account_user_name: str, verbose: bool = False):
        self.account_user_name = account_user_name
        self.verbose = verbose

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

from abc import abstractmethod


class Person:
    def __init__(self, account_user_name: str, verbose: bool = False):
        self.account_user_name = account_user_name
        self.verbose = verbose
        self.json_folder_path = None
        self.first_name = None
        self.last_name = None

    def get_account_user_name(self) -> str:
        """ get the account username """
        return self.account_user_name

    @abstractmethod
    def unpack_user_json_obj(self) -> None:
        """" unpack the user JSON obj must be implemented in subclass """
        pass

    def __str__(self) -> str:
        return_string = F"account_user_name : {self.account_user_name} \n"
        return_string += F"verbose           : {self.verbose}\n"
        return_string += F"first_name        : {self.first_name}\n"
        return_string += F"last_name         : {self.last_name}\n"
        return_string += F"json_folder_path  : {self.json_folder_path}\n"
        return return_string

    def __repr__(self) -> str:
        return self.__str__()


if __name__ == "__main__":
    p = Person(account_user_name="test")
    p.first_name = "John"
    p.last_name = "Doe"
    print(p)
    print(p.first_name)
    print(p.last_name)

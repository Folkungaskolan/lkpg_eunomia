from abc import abstractmethod


class Person:
    """
    @abstractmethod
    bygger skelett åt Student och staff_utils
    """

    def __init__(self, account_user_name: str, verbose: bool = False):
        self.verbose = verbose
        self.account_user_name = account_user_name
        self._first_name = None
        self._last_name = None

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
        return_string += F"first_name        : {self._first_name}\n"
        return_string += F"last_name         : {self._last_name}\n"
        return_string += F"json_folder_path  : {self.json_folder_path}\n"
        return return_string

    def __repr__(self) -> str:
        return self.__str__()


if __name__ == "__main__":
    p = Person(account_user_name="test")
    p._first_name = "John"
    p._last_name = "Doe"
    print(p)
    print(p._first_name)
    print(p._last_name)

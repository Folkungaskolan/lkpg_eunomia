""" Wrappers funktioner för förenkling sökvägs relaterade funktioner """

import os


def split_folder_path_from_filepath(filepath: str) -> str:
    """
    Givet en sökväg till en fil, returnera sökvägen till dess mapp
    :param filepath: str
    :return:
    """
    return os.path.dirname(filepath)


def split_filename_from_filepath(filepath: str) -> str:
    """
    Givet en sökväg till en fil, returnera filnamnet
    :param filepath: str
    :return: str
    """
    return os.path.basename(filepath)

def split_file_name_no_suffix_from_filepath(filepath: str) -> str:
    """ Returnera filnamnet utan suffix """
    return os.path.splitext(os.path.basename(filepath))[0]

def split_student_klass_from_filepath(filepath: str) -> str:
    """
    Givet en sökväg till en elev fil, returnera klassen
    :param filepath: str
    :return: str
    """
    return "_".join(os.path.basename(filepath).split("_")[:2])


def split_student_account_user_name_from_filepath(filepath: str) -> str:
    """
    Givet en sökväg till en elev fil, returnera användarnamnet
    :param filepath: str
    :return: str
    """
    return os.path.basename(filepath).split("_")[-1].split(".")[0]


def split_staff_account_user_name_from_filepath(filepath: str) -> str:
    """
    Givet en sökväg till en anställds fil, returnera användarnamnet
    :param filepath: str
    :return: str
    """
    return os.path.basename(filepath).split(".")[0]


def delete_file(filepath: str) -> None:
    """ Radera filen i sökvägen"""
    os.remove(filepath)


if __name__ == '__main__':
    pass

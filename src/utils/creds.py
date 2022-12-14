import json

from settings.folders import CRED_FOLDER_PATH


def get_cred(account_file_name: str) -> object:
    """ hämta fil"""
    with open(CRED_FOLDER_PATH + account_file_name + '.json', 'r') as fp:
        data = json.load(fp)
    fp.close()
    return data


def print_creds(account_file_name: str) -> None:
    creds = get_cred(account_file_name=account_file_name)
    print(creds)


def save_cred(account_file_name: str, creds: dict) -> None:
    with open(CRED_FOLDER_PATH + account_file_name + '.json', 'w') as fp:
        json.dump(creds, fp)
    fp.close()


if __name__ == "__main__":
    print_creds(account_file_name="lyam_windows_user")

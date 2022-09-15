from Student import Student
from utils import generate_and_save_eduroam_for_user

if __name__ == "__main__":
    s = Student(account_user_name="lyam", verbose=True)
    generate_and_save_eduroam_for_user(loc_account_user_name=s.get_account_user_name(), verbose=True)

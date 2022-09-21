from Student import Student


if __name__ == "__main__":
    s = Student(account_user_name="lyam", verbose=True)
    s.gen_eduroam_pw()
    s.print_eduroam_pw()
    s.gen_exelfiles()
    s.gen_csvfiles()

""" Generera Eduroam användare för elev """
from utils.file_utils.excel import write_student_csv_from_mysql
from utils.web_utils.eduroam_web_scraper import generate_eduroam_for_user


def gen_for(user_list: list[str]) -> None:
    """ generera eduroam för användare """
    for user in user_list:
        generate_eduroam_for_user(user_id=user)


if __name__ == '__main__':
    generate_eduroam_for_user(user_id="isasol996", headless_input_bool=True)

    # gen_for(user_list=["moafor351", "asmbrh065"])  # WORKS
    write_student_csv_from_mysql()

""" Generera Eduroam användare för elev """
from utils.file_utils.excel import write_student_csv_from_mysql
from utils.web_utils.eduroam_web_scraper import generate_eduroam_for_user


def gen_for(user_list: list[str]) -> None:
    """ generera eduroam för användare """
    for user in user_list:
        generate_eduroam_for_user(user_id=user)


if __name__ == '__main__':
    # generate_eduroam_for_user(user_id="edvpet613", headless_input_bool=False)
    # gen_for(user_list=["asmbrh065",
    #                    "edvpet613",
    #                    "mokboa436",
    #                    "sigand252"]
    #         )
    write_student_csv_from_mysql()

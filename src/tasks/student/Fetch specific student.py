from utils.web_utils.eduroam_web_scraper import generate_eduroam_for_user
from utils.web_utils.student_web_scraper import fetch_single_student_from_web

if __name__ == '__main__':
    user_id = "klaalw655"
    fetch_single_student_from_web(user_id=user_id)
    # generate_eduroam_for_user(user_id=user_id, headless_input_bool=True)
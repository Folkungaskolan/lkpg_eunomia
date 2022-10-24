""" hämta samtliga elever från weben """
from utils.web_utils.student_web_scraper import import_student_from_web


def get_ids() -> None:
    """ hämta samtliga id från webben """
    pass


def process_id_into_student_record() -> None:
    """ Hämta id json filer och hämta elev för varje sådan"""
    pass


def move_students_to_old_folder() -> None:
    """ generera eleven för respektive id """
    pass


if __name__ == "__main__":
    import_student_from_web()

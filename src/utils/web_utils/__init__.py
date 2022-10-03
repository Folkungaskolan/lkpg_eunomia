""" importer för web utils packetet """
from .eduroam_web_scraper import generate_eduroam_for_user

from .general_web import init_chrome_webdriver
from .general_web import init_firefox_webdriver

from .student_web_scraper import import_student_from_web

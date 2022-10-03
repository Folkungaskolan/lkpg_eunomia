"""
Hanterar generella webbrelaterade funktioner som inte är specifika till viss hemsida
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def init_firefox_webdriver(headless_bool: bool = None) -> webdriver:
    """		fixar inställningar för webdrivern		"""
    path = r'H:\Min enhet\selenium_browserdriver\geckodriver.exe'
    options = FirefoxOptions()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    if headless_bool is True:
        options.headless = True
    driver = webdriver.Firefox(executable_path=path, options=options)
    # driver.set_window_position(2560 + 1080, 355)
    driver.set_window_size(1000, 900)
    driver.implicitly_wait(10)  # seconds
    return driver


def init_chrome_webdriver(headless_bool: bool = True, enable_file_download_redirect: bool = False) -> webdriver:
    """		fixar inställningar för webdrivern		"""
    options = ChromeOptions()
    options.headless = headless_bool
    if enable_file_download_redirect:
        options.add_experimental_option("prefs", {"download.default_dirctory": r"H:\Min enhet\Python\Eunomia\downloads"})
    srv_obj = Service(executable_path=r'H:\Min enhet\selenium_browserdriver\chromedriver103.exe')
    driver = webdriver.Chrome(service=srv_obj, options=options)
    # driver.set_window_position(2560 + 1080, 355)
    driver.set_window_size(1000, 900)
    driver.implicitly_wait(10)  # seconds
    return driver

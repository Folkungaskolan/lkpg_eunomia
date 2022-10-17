"""
Hanterar generella webbrelaterade funktioner som inte är specifika till viss hemsida
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from settings.file_references import CHROME_DRIVER_EXEC, FIREFOX_DRIVER_EXEC


def init_firefox_webdriver(headless_bool: bool = None) -> webdriver:
    """		fixar inställningar för webdrivern		"""
    path = r'H:\Min enhet\selenium_browserdriver\geckodriver.exe'
    options = FirefoxOptions()
    options.binary_location = FIREFOX_DRIVER_EXEC
    if headless_bool is True:
        options.headless = True
    driver = webdriver.Firefox(executable_path=path, options=options)
    # driver.set_window_position(2560 + 1080, 355)
    driver.set_window_size(1000, 900)
    driver.implicitly_wait(10)  # seconds
    return driver


def init_chrome_webdriver(headless_bool: bool = True, file_download_redirect_to_folder: str = None) -> webdriver:
    """		fixar inställningar för webdrivern		"""
    options = ChromeOptions()
    options.headless = headless_bool
    if file_download_redirect_to_folder is not None:
        options.add_experimental_option("prefs", {"download.default_dirctory": file_download_redirect_to_folder})
    srv_obj = Service(executable_path=CHROME_DRIVER_EXEC)
    driver = webdriver.Chrome(service=srv_obj, options=options)
    # driver.set_window_position(2560 + 1080, 355)
    driver.set_window_size(1000, 900)
    driver.implicitly_wait(10)  # seconds
    return driver


SCREEN_POSITIONS = {1: {"x": 2560,
                        "y": 1920 - 1440,
                        "width": 1080,
                        "height": 1920 / 2},
                    2: {"x": 2560,
                        "y": 1440 - (1080 / 2),
                        "width": 1080,
                        "height": 1920 / 2},
                    3: {"x": 2560 + 1080,
                        "y": 1440 - 1080,
                        "width": 1920 / 2,
                        "height": 1080},
                    4: {"x": 2560 + 1080 + (1920 / 2),
                        "y": 1440 - 1080 + (1920 / 2),
                        "width": 1920 / 2,
                        "height": 1080}
                    }

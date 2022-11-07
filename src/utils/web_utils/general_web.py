"""
Hanterar generella webbrelaterade funktioner som inte är specifika till viss hemsida
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from settings.file_references import CHROME_DRIVER_EXEC, FIREFOX_DRIVER_EXEC, FIREFOX_SELENIUM_DRIVER_EXEC


def init_firefox_webdriver(headless_bool: bool = None) -> webdriver:
    """		fixar inställningar för webdrivern		"""
    path = FIREFOX_SELENIUM_DRIVER_EXEC
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
    # https://stackoverflow.com/questions/47392423/python-selenium-devtools-listening-on-ws-127-0-0-1
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if file_download_redirect_to_folder is not None:
        options.add_experimental_option("prefs", {"download.default_dirctory": file_download_redirect_to_folder})
    srv_obj = Service(executable_path=CHROME_DRIVER_EXEC)
    driver = webdriver.Chrome(service=srv_obj, options=options)
    # driver.set_window_position(2560 + 1080, 355)
    driver.set_window_size(1000, 900)
    driver.implicitly_wait(10)  # seconds
    return driver


def position_windows(driver: webdriver, position_nr: int = 1) -> webdriver:
    """
    Positionerar fönstret på skärmen
    :param driver:
    :param position_nr: 1 till 4
    :return:
    """
    SCREEN_POSITIONS = {1: {"x": 2560,
                            "y": int(-(1920 - 1440)),
                            "width": 1080,
                            "height": int(1920 / 2)},
                        2: {"x": 2560,
                            "y": int(1440 - (1920 / 2)),
                            "width": 1080,
                            "height": 900},
                        3: {"x": int(2560 + 1080),
                            "y": int(1440 - 1080),
                            "width": int(1920 / 2),
                            "height": 1000},
                        4: {"x": int(2560 + 1080 + (1920 / 2)),
                            "y": int(1440 - 1080),
                            "width": int(1920 / 2),
                            "height": 1000}
                        }
    driver.set_window_position(SCREEN_POSITIONS[position_nr]["x"], SCREEN_POSITIONS[position_nr]["y"])
    driver.set_window_size(SCREEN_POSITIONS[position_nr]["width"], SCREEN_POSITIONS[position_nr]["height"])
    return driver


if __name__ == '__main__':
    driver1 = init_chrome_webdriver(headless_bool=False)
    position_windows(driver1, 1)
    driver2 = init_chrome_webdriver(headless_bool=False)
    position_windows(driver2, 2)
    driver3 = init_chrome_webdriver(headless_bool=False)
    position_windows(driver3, 3)
    driver4 = init_chrome_webdriver(headless_bool=False)
    position_windows(driver4, 4)
    pass

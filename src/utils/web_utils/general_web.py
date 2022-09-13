def init_firefox_webdriver(headless_bool: bool = None) -> webdriver:
    """		fixar inställningar för webdrivern		"""
    path = r'H:\Min enhet\selenium_browserdriver\geckodriver.exe'
    options = firefox_options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    if headless_bool is True:
        options.headless = True
    driver = webdriver.Firefox(executable_path=r'H:\Min enhet\selenium_browserdriver\geckodriver.exe', options=options)
    # driver.set_window_position(2560 + 1080, 355)
    driver.set_window_size(1000, 900)
    driver.implicitly_wait(10)  # seconds
    return driver

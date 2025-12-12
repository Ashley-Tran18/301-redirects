# base/basepage.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 10

    def open(self, url):
        self.driver.get(url)

    def current_url(self):
        return self.driver.current_url
    
    def wait_for_url_change(self, old_url, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.current_url != old_url
        )

    
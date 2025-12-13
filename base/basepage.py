# base/basepage.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, urlunparse
import re


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

    def normalize_url(self, url: str) -> str:
        url = url.strip()
        parsed = urlparse(url)
        path = parsed.path if parsed.path else '/'
        
        # Collapse tất cả multiple slashes thành single
        path = re.sub(r'/+', '/', path)
        
        # Loại bỏ trailing slash (trừ root)
        path = path.rstrip('/') if path != '/' else '/'
        
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.params,
            parsed.query,
            ''
        ))
        return normalized
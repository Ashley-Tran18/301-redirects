# base/basepage.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse, urlunparse, unquote, quote
import re


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 10

    def open(self, url):
        self.driver.get(url)

    def current_url(self):
        return self.driver.current_url
    
    def wait_for_url_change(self, old_url, timeout=10):  # Add a sensible timeout, e.g. 30s
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.current_url != old_url
            )
        except TimeoutException:
            # If no change after timeout, assume it's intentional (no redirect)
            # You can log or just proceed – the assertion will catch mismatches
            pass


    # def normalize_url(self, url: str) -> str:
    #     url = url.strip()
    #     parsed = urlparse(url)
    #     path = parsed.path if parsed.path else '/'
        
    #     # Collapse tất cả multiple slashes thành single
    #     path = re.sub(r'/+', '/', path)
        
    #     # Loại bỏ trailing slash (trừ root)
    #     path = path.rstrip('/') if path != '/' else '/'
        
    #     normalized = urlunparse((
    #         parsed.scheme.lower(),
    #         parsed.netloc.lower(),
    #         path,
    #         parsed.params,
    #         parsed.query,
            
    #         ''
    #     ))
    #     return normalized
    


    def normalize_url(self, url: str) -> str:
        if not url:
            return ""

        url = url.strip()
        parsed = urlparse(url)

        path = parsed.path if parsed.path else '/'

        # Decode rồi encode lại để chuẩn hóa Unicode (®, é, ü...)
        path = quote(unquote(path), safe="/+:")

        # Collapse multiple slashes thành single
        path = re.sub(r'/+', '/', path)

        # Loại bỏ trailing slash (trừ root)
        path = path.rstrip('/') if path != '/' else '/'

        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            "",              # params (không dùng)
            parsed.query,    # giữ query (?p=3)
            ""               # fragment
        ))

        return normalized


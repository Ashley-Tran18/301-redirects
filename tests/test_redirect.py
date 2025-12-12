# tests/test_redirect.py
import pandas as pd
import os
import pytest
import allure
from urllib.parse import urlparse
from base.basetest import BaseTest
from base.basepage import BasePage
from allure_commons.types import AttachmentType
from urllib.parse import urlparse, urlunparse
import requests
import re


# === SAFER EXCEL LOADING ===
csv_path = os.path.join(os.path.dirname(__file__), "..", "redirect_mapping.csv")

print(f"Loading CSV from: {csv_path}")
print("Files in directory:", os.listdir(os.path.dirname(csv_path)))

# Load redirect mapping from Excel
df = pd.read_csv("redirect_mapping.csv" )


# def normalize_url(url: str) -> str:
#     url = url.strip()
#     parsed = urlparse(url)
#     # Loại bỏ trailing slash ở path (trừ root /)
#     path = parsed.path.rstrip('/') if parsed.path != '/' else '/'
#     # Xây lại URL sạch
#     normalized = urlunparse((
#         parsed.scheme.lower(),
#         parsed.netloc.lower(),
#         path,
#         parsed.params,
#         parsed.query,
#         ''  # Bỏ fragment nếu không cần
#     ))
#     return normalized

def normalize_url(url: str) -> str:
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

@pytest.mark.usefixtures("driver")
class TestRedirects(BaseTest):

    @pytest.mark.parametrize("row", df.to_dict("records"))
    @allure.title("Verify redirect: {row[Staging URL]} → {row[Redirected To (Staging URLs)]}")
    def test_redirects(self, row):
        staging_url = str(row["Staging URL"]).strip()
        expected_redirect = str(row["Redirected To (Staging URLs)"]).strip()
      
         # Step 1: Open the staging URL and take screenshot
        with allure.step(f"Step 1: Navigate to staging URL - {staging_url}"):
            page = BasePage(self.driver)
            page.open(staging_url)
            allure.attach(
                body=self.driver.get_screenshot_as_png(),
                name="Screenshot: After loading staging URL",
                attachment_type=AttachmentType.PNG
            )

        # Chờ redirect
        page.wait_for_url_change(staging_url)

        # Lấy URL cuối cùng
        actual_url = page.current_url()

        try:
            response = requests.get(staging_url, allow_redirects=True, timeout=10)
            http_final_url = response.url
            history_status = [f"{r.status_code} -> {r.url}" for r in response.history]
            with allure.step(f"HTTP redirect chain (requests): {' -> '.join(history_status + [http_final_url])}"):
                pass
        except Exception as e:
            with allure.step(f"Requests failed: {e}"):
                pass


        actual_url_norm = normalize_url(actual_url)
        expected_norm = normalize_url(expected_redirect)

        assert actual_url_norm == expected_norm, \
            f"\n❌ Redirect mismatch!\nExpected: {expected_norm}\nActual: {actual_url_norm}\nOriginal Actual: {actual_url}"

     

       

       
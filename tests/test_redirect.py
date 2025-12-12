# tests/test_redirect.py
import pandas as pd
import os
import pytest
import allure
from urllib.parse import urlparse
from base.basetest import BaseTest
from base.basepage import BasePage
from allure_commons.types import AttachmentType


# === SAFER EXCEL LOADING ===
csv_path = os.path.join(os.path.dirname(__file__), "..", "redirect_mapping.csv")

print(f"Loading CSV from: {csv_path}")
print("Files in directory:", os.listdir(os.path.dirname(csv_path)))

# Load redirect mapping from Excel
df = pd.read_csv("redirect_mapping.csv" )

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

        with allure.step(f"Final URL after redirect = {actual_url}"):
            pass

        # Normalize để tránh lỗi //// 
        actual_url_norm = actual_url.replace("//", "/").replace("https:/", "https://")
        expected_norm = expected_redirect.replace("//", "/").replace("https:/", "https://")

        assert actual_url_norm == expected_norm, \
            f"\n❌ Redirect mismatch!\nExpected: {expected_norm}\nActual:   {actual_url_norm}\n"

     


     


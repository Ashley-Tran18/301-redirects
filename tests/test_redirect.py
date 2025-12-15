# # tests/test_redirect.py
# import pandas as pd
# import os
# import pytest
# import allure
# from base.basetest import BaseTest
# from base.basepage import BasePage
# from allure_commons.types import AttachmentType
# import requests



# # === SAFER EXCEL LOADING ===
# csv_path = os.path.join(os.path.dirname(__file__), "..", "redirect_mapping.csv")

# print(f"Loading CSV from: {csv_path}")
# print("Files in directory:", os.listdir(os.path.dirname(csv_path)))

# # Load redirect mapping from CSV
# df = pd.read_csv("redirect_mapping.csv" )

# @pytest.mark.usefixtures("driver")
# class TestRedirects(BaseTest):

#     @pytest.mark.parametrize("row", df.to_dict("records"))
#     @allure.title("Verify redirect: {row[Staging URL]} → {row[Redirected To (Staging URLs)]}")
#     def test_redirects(self, row):
#         staging_url = str(row["Staging URL"]).strip()
#         expected_redirect = str(row["Redirected To (Staging URLs)"]).strip()
      
#          # Step 1: Open the staging URL and take screenshot
#         with allure.step(f"Step 1: Navigate to staging URL - {staging_url}"):
#             page = BasePage(self.driver)
#             page.open(staging_url)
#             allure.attach(
#                 body=self.driver.get_screenshot_as_png(),
#                 name="Screenshot: After loading staging URL",
#                 attachment_type=AttachmentType.PNG
#             )

#         # Chờ redirect
#         page.wait_for_url_change(staging_url)

#         # Lấy URL cuối cùng
#         actual_url = page.current_url()

#         try:
#             response = requests.get(staging_url, allow_redirects=True, timeout=10)
#             http_final_url = response.url
#             history_status = [f"{r.status_code} -> {r.url}" for r in response.history]
#             with allure.step(f"HTTP redirect chain (requests): {' -> '.join(history_status + [http_final_url])}"):
#                 pass
#         except Exception as e:
#             with allure.step(f"Requests failed: {e}"):
#                 pass

#         actual_url_norm = page.normalize_url(actual_url)
#         expected_norm = page.normalize_url(expected_redirect)

#         assert actual_url_norm == expected_norm, \
#             f"\n❌ Redirect mismatch!\nExpected: {expected_norm}\nActual: {actual_url_norm}\nOriginal Actual: {actual_url}"

     
# tests/test_redirect.py
import pandas as pd
import os
import pytest
import allure
from base.basetest import BaseTest
from base.basepage import BasePage
from allure_commons.types import AttachmentType
import requests

# === SAFER CSV LOADING ===
csv_path = os.path.join(os.path.dirname(__file__), "..", "redirect_mapping.csv")
df = pd.read_csv(csv_path)

BATCH_SIZE = 200  # số URL trong mỗi batch

def chunkify(lst, n):
    """Chia list lst thành các chunk có kích thước n"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

batches = list(chunkify(df.to_dict("records"), BATCH_SIZE))

@pytest.mark.usefixtures("driver")
class TestRedirects(BaseTest):

    @pytest.mark.parametrize("batch_index,batch", [(i, b) for i, b in enumerate(batches)])
    @allure.title("Verify redirect batch {batch_index}")
    def test_redirect_batch(self, batch_index, batch):
        page = BasePage(self.driver)

        for row in batch:
            staging_url = str(row["Staging URL"]).strip()
            expected_redirect = str(row["Redirected To (Staging URLs)"]).strip()

            with allure.step(f"Navigate to staging URL: {staging_url}"):
                page.open(staging_url)
                # allure.attach(
                #     body=self.driver.get_screenshot_as_png(),
                #     name=f"Screenshot: {staging_url}",
                #     attachment_type=AttachmentType.PNG
                # )

            page.wait_for_url_change(staging_url)
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

            actual_url_norm = page.normalize_url(actual_url)
            expected_norm = page.normalize_url(expected_redirect)

            assert actual_url_norm == expected_norm, \
                f"\n❌ Redirect mismatch!\nExpected: {expected_norm}\nActual: {actual_url_norm}\nOriginal Actual: {actual_url}"

       

       
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

BATCH_SIZE = 500  # số URL trong mỗi batch

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
                allure.attach(
                    body=self.driver.get_screenshot_as_png(),
                    name=f"Screenshot: {staging_url}",
                    attachment_type=AttachmentType.PNG
                )

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

       

# # tests/test_redirect.py
# import os
# import math
# import csv
# import pandas as pd
# import pytest
# import allure
# import requests
# from urllib.parse import urljoin, urlparse
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry

# from base.basetest import BaseTest

# # ================= CONFIG =================
# CSV_FILE = os.path.join(os.path.dirname(__file__), "..", "redirect_mapping.csv")
# BATCH_SIZE = 500
# TIMEOUT = 15
# FAILED_DIR = os.path.join(os.path.dirname(__file__), "..", "failed")

# os.makedirs(FAILED_DIR, exist_ok=True)

# # ================= HELPERS =================

# def normalize_url(url: str) -> str:
#     if not url:
#         return ""

#     url = str(url).strip()

#     parsed = urlparse(url)

#     scheme = parsed.scheme.lower()
#     netloc = parsed.netloc.lower()
#     path = parsed.path.rstrip("/")

#     return f"{scheme}://{netloc}{path}"


# def resolve_location(source_url: str, location: str) -> str:
#     """
#     Convert relative Location -> absolute URL
#     """
#     if not location:
#         return ""
#     if location.startswith("/"):
#         return urljoin(source_url, location)
#     return location


# def load_csv():
#     df = pd.read_csv(CSV_FILE)
#     return df.fillna("")


# def get_batch(df: pd.DataFrame, chunk: int):
#     total = len(df)
#     total_chunks = math.ceil(total / BATCH_SIZE)

#     if chunk < 1 or chunk > total_chunks:
#         # Thay vì skip và gây exit code 5, chỉ warning và return empty
#         print(f"WARNING: Chunk {chunk} out of range (1-{total_chunks}). No tests to run.")
#         return pd.DataFrame(), total_chunks  # Trả về DataFrame rỗng

#     start = (chunk - 1) * BATCH_SIZE
#     end = start + BATCH_SIZE

#     return df.iloc[start:end], total_chunks


# # ================= REQUEST SESSION =================

# def create_retry_session():
#     session = requests.Session()
#     retry = Retry(
#         total=3,
#         backoff_factor=1,
#         status_forcelist=[429, 500, 502, 503, 504],
#         allowed_methods=["GET"]
#     )
#     adapter = HTTPAdapter(max_retries=retry)
#     session.mount("http://", adapter)
#     session.mount("https://", adapter)
#     return session


# # ================= PYTEST PARAM =================

# def pytest_generate_tests(metafunc):
#     if "row" not in metafunc.fixturenames:
#         return

#     chunk_opt = metafunc.config.getoption("--chunk")
#     chunk = int(chunk_opt) if chunk_opt else None

#     df = load_csv()

#     if chunk is None:
#         batch_df = df
#     else:
#         batch_df, total_chunks = get_batch(df, chunk)
#         print(f"Running chunk {chunk}/{total_chunks} with {len(batch_df)} tests")

#     if len(batch_df) == 0:
#         # Không parametrize gì cả → pytest sẽ báo "no tests ran" nhưng exit code 0
#         return

#     records = batch_df.to_dict("records")
#     ids = [f"row{i+1}" for i in range(len(records))]

#     metafunc.parametrize("row", records, ids=ids)
# # ================= FIXTURES =================

# @pytest.fixture(scope="session")
# def http_session():
#     return create_retry_session()


# @pytest.fixture(scope="session")
# def failed_writer(request):
#     chunk = request.config.getoption("--chunk") or "1"
#     failed_file = os.path.join(FAILED_DIR, f"failed_chunk_{chunk}.csv")

#     file = open(failed_file, mode="w", newline="", encoding="utf-8")
#     writer = csv.DictWriter(file, fieldnames=[
#         "source_url", "expected_url", "actual_location", "status_code", "reason"
#     ])
#     writer.writeheader()

#     yield writer
#     file.close()


# # ================= TEST =================

# @allure.epic("SEO")
# @allure.feature("301 Redirect Validation")
# class TestRedirects(BaseTest):

#     @allure.story("Verify redirect destination")
#     def test_redirect(self, row, http_session, failed_writer):
#         source = row.get("staging_url") or row.get("Staging URL") or row.get("Page URL")
#         expected = row.get("expected_url") or row.get("Redirected To (Staging URLs)") or row.get("Redirected To")

#         allure.dynamic.parameter("source_url", source)
#         allure.dynamic.parameter("expected_url", expected)

#         try:
#             response = http_session.get(
#                 source,
#                 allow_redirects=False,
#                 timeout=TIMEOUT
#             )

#             if response.status_code in (301, 302):
#                 raw_location = response.headers.get("Location", "")
#                 actual = resolve_location(source, raw_location)
#                 status_code = response.status_code
#             else:
#                 final_resp = http_session.get(
#                     source,
#                     allow_redirects=True,
#                     timeout=TIMEOUT
#                 )
#                 actual = final_resp.url
#                 status_code = final_resp.status_code

#             assert normalize_url(actual) == normalize_url(expected), (
#                 f"Redirect mismatch\n"
#                 f"Actual:   {actual}\n"
#                 f"Expected: {expected}"
#             )

#         except AssertionError as e:
#             failed_writer.writerow({
#                 "source_url": source,
#                 "expected_url": expected,
#                 "actual_location": actual if 'actual' in locals() else "",
#                 "status_code": status_code if 'status_code' in locals() else "",
#                 "reason": str(e)
#             })
#             raise

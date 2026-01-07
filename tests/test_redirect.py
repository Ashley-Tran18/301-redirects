# tests/test_redirect.py
import pandas as pd
import os
import pytest
import allure
import requests
from base.basetest import BaseTest
from base.basepage import BasePage
from allure_commons.types import AttachmentType


# === CSV LOADING ===
csv_path = os.path.join(os.path.dirname(__file__), "..", "redirect_mapping.csv")
df = pd.read_csv(csv_path)

redirect_cases = [
    pytest.param(
        str(row["Staging URL"]).strip(),
        str(row["Redirected To (Staging URLs)"]).strip(),
        id=f"{str(row['Staging URL']).strip()} → {str(row['Redirected To (Staging URLs)']).strip()}"
    )
    for _, row in df.iterrows()
]

@pytest.mark.usefixtures("driver")
class TestRedirects(BaseTest):

    @pytest.mark.parametrize("staging_url, expected_url", redirect_cases)
    @allure.title("Verify redirect batch {staging_url}")
    def test_redirect(self, staging_url, expected_url):
        page = BasePage(self.driver)

        page.open(staging_url)
        page.wait_for_url_change(staging_url)
        actual_url = page.current_url()


        # --- HTTP redirect chain (for debugging) ---
        try:
            response = requests.get(
                staging_url,
                allow_redirects=True,
                timeout=10
            )
            chain = [f"{r.status_code} → {r.url}" for r in response.history]
            chain.append(response.url)

            with allure.step("HTTP redirect chain (requests)"):
                allure.attach(
                    "\n".join(chain),
                    name="Redirect chain",
                    attachment_type=AttachmentType.TEXT
                )
        except Exception as e:
            with allure.step(f"Requests failed: {e}"):
                pass

        # === ASSERT & ALLURE HANDLING ===
        # if actual_url != expected_url:
        #     allure.label("redirect_status", "FAILED")

        #     allure.attach(
        #         f"""
        # ❌ Redirect mismatch

        # From: {staging_url}
        # Expected: {expected_url}
        # Actual: {actual_url}
        #         """,
        #         name="❌ Redirect mismatch",
        #         attachment_type=AttachmentType.TEXT
        #     )

        #     pytest.fail(f"Redirect mismatch: {staging_url}")

        assert actual_url == expected_url, (
            f"\n❌ Redirect mismatch"
            f"\nFrom: {staging_url}"
            f"\nExpected: {expected_url}"
            f"\nActual: {actual_url}"
        )


          
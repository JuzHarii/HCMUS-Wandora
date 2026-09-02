from uuid import uuid4

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT, SELECTORS
from pages.trip_creation_page import TripCreationPage


def _fill_valid_trip(page, destination=None):
    page.fill_trip_form(
        destination=destination or f"PA5 Da Nang {uuid4().hex[:6]}",
        start_date="2026-09-01",
        end_date="2026-09-03",
        capacity="4",
        budget="3000000",
    )


def test_tc_uc01_01_successful_trip_creation_reaches_review(authenticated_driver):
    page = TripCreationPage(authenticated_driver).open_trip_creation()
    _fill_valid_trip(page)
    page.submit_details()

    WebDriverWait(authenticated_driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["trip_review_ready"]))
    )
    assert page.wait_visible(SELECTORS["generate_preview_button"]).is_enabled()


def test_tc_uc01_03_invalid_date_order_blocks_submission(authenticated_driver):
    page = TripCreationPage(authenticated_driver).open_trip_creation()
    page.fill_trip_form(
        destination="Tokyo",
        start_date="2026-09-10",
        end_date="2026-09-01",
        capacity="2",
    )
    page.submit_details()

    assert "end date must be after or equal to start date" in page.get_validation_alert_text().lower()

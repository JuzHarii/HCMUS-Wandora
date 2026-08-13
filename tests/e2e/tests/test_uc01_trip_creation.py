"""Browser-level PA4 tests for UC01 - Trip Creation and Preference Input."""

import os
import sys
from uuid import uuid4

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import AI_TIMEOUT, BASE_URL, SELECTORS
from pages.trip_creation_page import TripCreationPage


def _valid_trip(page: TripCreationPage, destination: str | None = None) -> None:
    page.fill_trip_form(
        destination=destination or f"PA4 Da Nang {uuid4().hex[:6]}",
        start_date="2026-09-01",
        end_date="2026-09-03",
        capacity="4",
        budget="3000000",
        style="Cultural",
    )


def test_uc01_01_successful_trip_creation(authenticated_driver):
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    destination = f"PA4 Da Nang {uuid4().hex[:6]}"
    _valid_trip(page, destination)
    page.submit()
    page.generate_preview()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"])))
    page.save_trip()
    page.open_saved_trip()

    WebDriverWait(driver, AI_TIMEOUT).until(EC.url_contains("/trips/"))
    driver.get(f"{BASE_URL}/home")
    cards = WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_all_elements_located(("css selector", SELECTORS["dashboard_trip_card"]))
    )
    assert any(destination in card.text for card in cards)


def test_uc01_02_missing_destination_blocks_submission(authenticated_driver):
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(start_date="2026-09-01", end_date="2026-09-03", capacity="2")
    page.submit()

    assert "destination" in page.get_validation_alert_text().lower()


def test_uc01_03_missing_dates_blocks_submission(authenticated_driver):
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(destination="Tokyo", capacity="2")
    page.submit()

    assert "start date" in page.get_validation_alert_text().lower()


def test_uc01_04_end_date_before_start_date_is_rejected(authenticated_driver):
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(destination="London", start_date="2026-09-10", end_date="2026-09-01", capacity="2")
    page.submit()

    assert "end date must be after or equal" in page.get_validation_alert_text().lower()


def test_uc01_05_invalid_group_size_is_rejected(authenticated_driver):
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(destination="Hue", start_date="2026-09-01", end_date="2026-09-03", capacity="0")
    page.submit()

    assert "at least 1 traveler" in page.get_validation_alert_text().lower()

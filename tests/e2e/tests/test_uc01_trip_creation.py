"""Browser-level PA4 tests for UC01 - Trip Creation and Preference Input."""

import os
import sys
from uuid import uuid4

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import AI_TIMEOUT, BASE_URL, DEFAULT_TIMEOUT
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
    assert page.generate_preview()


def test_uc01_02_missing_required_fields(authenticated_driver):
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(start_date="2026-09-01", end_date="2026-09-03", capacity="2")
    page.submit()
    assert "choose a destination" in page.get_validation_alert_text().lower()


def test_uc01_03_invalid_date_order(authenticated_driver):
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(destination="Tokyo", start_date="2026-09-10", end_date="2026-09-01", capacity="2")
    page.submit()
    assert "end date must be after or equal to start date" in page.get_validation_alert_text().lower()


def test_uc01_04_access_control_interception_for_guest_users(driver):
    driver.get(f"{BASE_URL}/trips/new")
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.url_contains("/auth?mode=login"))
    assert "next=%2Ftrips%2Fnew" in driver.current_url

def test_uc01_05_numeric_boundary_check_on_group_size(authenticated_driver):
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(destination="London", start_date="2026-09-01", end_date="2026-09-05", capacity="-3")
    page.submit()
    assert "at least 1" in page.get_validation_alert_text().lower()
 

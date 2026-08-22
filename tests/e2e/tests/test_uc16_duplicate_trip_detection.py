"""Browser-level PA4 tests for UC16 - Duplicate/Similar Trip Detection."""

import os
import sys
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.dashboard_page import DashboardPage
from pages.trip_creation_page import TripCreationPage
from helpers import create_saved_trip


def _create_existing_paris_trip(driver):
    return create_saved_trip(
        driver,
        destination="Paris",
        start_date="2026-10-01",
        end_date="2026-10-10",
    )


def test_uc16_01_similar_trip_detected_warning(authenticated_driver):
    """TC_UC16_01 - Similar Trip Detected Warning (Basic Flow)."""
    driver = authenticated_driver
    _create_existing_paris_trip(driver)

    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(destination="Paris", start_date="2026-10-03", end_date="2026-10-08", capacity="2")
    page.submit()

    assert page.similar_trip_modal_is_present(timeout=5), "Overlapping destination/dates should trigger the similar-trip modal"
    assert "similar trip" in driver.page_source.lower()


def test_uc16_02_use_similar_trip_as_template(authenticated_driver):
    """TC_UC16_02 - Use Similar Trip as Template (Basic Flow - Template Select)."""
    driver = authenticated_driver
    _create_existing_paris_trip(driver)

    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(destination="Paris", start_date="2026-10-03", end_date="2026-10-08", capacity="2")
    page.submit()
    WebDriverWait(driver, AI_TIMEOUT).until(lambda d: page.similar_trip_modal_is_present(timeout=5))

    dashboard = DashboardPage(driver)
    dashboard.use_similar_trip_as_template()

    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"]))
    )


def test_uc16_03_open_existing_match_trip(authenticated_driver):
    """TC_UC16_03 - Open Existing Match Trip (Basic Flow - Redirect Option)."""
    driver = authenticated_driver
    _create_existing_paris_trip(driver)
    existing_url = driver.current_url

    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(destination="Paris", start_date="2026-10-03", end_date="2026-10-08", capacity="2")
    page.submit()
    WebDriverWait(driver, AI_TIMEOUT).until(lambda d: page.similar_trip_modal_is_present(timeout=5))

    dashboard = DashboardPage(driver)
    dashboard.open_existing_similar_trip()

    WebDriverWait(driver, AI_TIMEOUT).until(EC.url_contains("/trips/"))
    assert driver.current_url.split("?")[0] == existing_url.split("?")[0]


def test_uc16_04_force_continue_as_new(authenticated_driver):
    """TC_UC16_04 - Force Continue as New (Basic Flow - Bypass Option)."""
    driver = authenticated_driver
    _create_existing_paris_trip(driver)

    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(destination="Paris", start_date="2026-10-03", end_date="2026-10-08", capacity="2")
    page.submit()
    WebDriverWait(driver, AI_TIMEOUT).until(lambda d: page.similar_trip_modal_is_present(timeout=5))

    dashboard = DashboardPage(driver)
    dashboard.continue_as_new_trip()

    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["generate_preview_button"]))
    )


def test_uc16_05_no_overlaps_found_proceed(authenticated_driver):
    """TC_UC16_05 - No Overlaps Found Proceed (Alternative Flow 1)."""
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(
        destination=f"PA4 UC16 No Overlap {uuid4().hex[:6]}",
        start_date="2026-11-01",
        end_date="2026-11-05",
        capacity="2",
    )
    page.submit()

    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["generate_preview_button"]))
    )
    assert not page.similar_trip_modal_is_present(timeout=2)
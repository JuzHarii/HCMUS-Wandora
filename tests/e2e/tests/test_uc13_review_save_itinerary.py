"""Browser-level PA4 tests for UC13 - Review and Save AI Itinerary."""

import os
import sys
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, BASE_URL, SELECTORS
from pages.trip_creation_page import TripCreationPage


def _valid_trip_to_preview(page):
    page.fill_trip_form(
        destination=f"PA4 UC13 {uuid4().hex[:6]}",
        start_date="2026-09-01",
        end_date="2026-09-03",
        capacity="4",
        budget="3000000",
        style="Cultural",
    )
    page.submit()
    page.generate_preview()


def test_uc13_01_success_review_and_save_itinerary(authenticated_driver):
    """TC_UC13_01 - Success Review and Save Itinerary (Basic Flow)."""
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    _valid_trip_to_preview(page)
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"])))

    page.save_trip()
    page.open_saved_trip()

    WebDriverWait(driver, AI_TIMEOUT).until(EC.url_contains("/trips/"))
    assert "planning" in page.get_trip_status().lower()


def test_uc13_02_edit_preview_activity_before_saving(authenticated_driver):
    """TC_UC13_02 - Edit preview activity before saving (Basic Flow - Edit Option)."""
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    _valid_trip_to_preview(page)
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"])))

    page.edit_preview_activity(activity_index=0, new_text="Manually inserted breakfast stop")
    assert "Manually inserted" in page.get_preview_activity_texts()[0]

    page.save_trip()
    page.open_saved_trip()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_view"])))
    assert any(
        "Manually inserted" in row.text for row in driver.find_elements("css selector", SELECTORS["activity_row"])
    )


def test_uc13_03_return_to_details(authenticated_driver):
    """TC_UC13_03 - Return to details (Alternative Flow 1)."""
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    destination = f"PA4 UC13 Back {uuid4().hex[:6]}"
    page.fill_trip_form(
        destination=destination,
        start_date="2026-09-01",
        end_date="2026-09-03",
        capacity="4",
        budget="3000000",
        style="Cultural",
    )
    page.submit()
    page.generate_preview()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"])))

    page.back_to_details()

    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["trip_form"])))
    assert driver.find_element("css selector", SELECTORS["trip_destination_input"]).get_attribute("value") == destination


def test_uc13_04_leave_preview_without_saving(authenticated_driver):
    """TC_UC13_04 - Leave preview without saving (Alternative Flow 2)."""
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    _valid_trip_to_preview(page)
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"])))

    page.leave_preview_without_saving()
    assert "not be saved" in page.get_leave_preview_warning_text().lower()

    page.confirm_leave_preview()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["trip_dashboard"])))
    assert driver.current_url.rstrip("/").endswith("/home")


def test_uc13_05_access_preview_without_generated_itinerary(authenticated_driver):
    """TC_UC13_05 - Access preview without generated itinerary check."""
    driver = authenticated_driver
    driver.get(f"{BASE_URL}/itinerary/preview")

    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["trip_form"])))
    assert driver.current_url.rstrip("/").endswith("/trips/new") or "trips/new" in driver.current_url
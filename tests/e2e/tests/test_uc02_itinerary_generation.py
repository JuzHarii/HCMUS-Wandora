from uuid import uuid4

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, DEFAULT_TIMEOUT, SELECTORS
from pages.trip_creation_page import TripCreationPage


def _submit_valid_trip(driver, destination_prefix="PA5 Hoi An"):
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(
        destination=f"{destination_prefix} {uuid4().hex[:6]}",
        start_date="2026-09-01",
        end_date="2026-09-03",
        capacity="3",
        budget="2500000",
    )
    page.submit_details()
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["trip_review_ready"]))
    )
    return page


def test_tc_uc02_01_successful_ai_preview_generation(authenticated_driver):
    page = _submit_valid_trip(authenticated_driver)
    page.generate_preview()

    WebDriverWait(authenticated_driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"]))
    )
    assert page.preview_activity_rows(), "Expected generated itinerary preview activities"


def test_tc_uc02_03_blank_itinerary_can_be_saved(authenticated_driver):
    page = _submit_valid_trip(authenticated_driver, "PA5 Blank Schedule")
    page.start_blank_itinerary()

    WebDriverWait(authenticated_driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"]))
    )
    assert page.preview_day_cards(), "Expected blank day cards for the trip date range"
    assert not page.preview_activity_rows(), "Blank itinerary should start without activities"

    page.save_trip()
    page.open_saved_trip()
    WebDriverWait(authenticated_driver, DEFAULT_TIMEOUT).until(EC.url_contains("/trips/"))
    WebDriverWait(authenticated_driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_view"]))
    )

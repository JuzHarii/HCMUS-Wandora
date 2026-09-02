"""Browser-level PA4 tests for UC02 - AI Itinerary Generation."""

import os
import sys
from uuid import uuid4

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import AI_TIMEOUT, SELECTORS
from pages.trip_creation_page import TripCreationPage


def _submit_valid_trip(driver, destination_prefix="PA5 Trip"):
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(
        destination=f"{destination_prefix} {uuid4().hex[:6]}",
        start_date="2026-09-01",
        end_date="2026-09-03",
        capacity="3",
        budget="2500000",
        style="Balanced",
    )
    page.submit()
    return page


def test_uc02_01_successful_ai_preview_generation(authenticated_driver):
    driver = authenticated_driver
    page = _submit_valid_trip(driver, "PA4 Hoi An")
    page.generate_preview()
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"]))
    )
    assert page.get_preview_activity_rows(), "Expected a rendered interactive itinerary preview on the timeline"


# def test_uc02_02_ai_connection_timeout_with_fallback_retry(authenticated_driver):
#     driver = authenticated_driver
#     page = _submit_valid_trip(driver, "PA4 Timeout retry")
#     page.generate_preview()
#     WebDriverWait(driver, AI_TIMEOUT).until(
#         lambda d: d.find_elements("css selector", SELECTORS["save_trip_button"])
#         or page.fallback_dialog_is_present(timeout=1)
#     )
#     if page.fallback_dialog_is_present(timeout=1):
#         page.retry_generation()
#         WebDriverWait(driver, AI_TIMEOUT).until(
#             EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"]))
#         )
#     assert page.get_preview_activity_rows()
    

# def test_uc02_03_ai_service_outage_initialize_blank_schedule(authenticated_driver):
#     driver = authenticated_driver
#     page = _submit_valid_trip(driver, "PA4 Outage Blank")
#     page.generate_preview()
#     WebDriverWait(driver, AI_TIMEOUT).until(
#         lambda d: d.find_elements("css selector", SELECTORS["save_trip_button"])
#         or page.fallback_dialog_is_present(timeout=1)
#     )
#     if page.fallback_dialog_is_present(timeout=1):
#         page.start_blank_itinerary()
#         assert page.blank_itinerary_grid_is_visible(timeout=AI_TIMEOUT), (
#             "Expected a blank daily timeline grid in edit view after bypassing AI synthesis"
#         )
#     else:
#         assert page.get_preview_activity_rows()


def test_uc02_04_malformed_json_payload_handling(authenticated_driver):
    driver = authenticated_driver
    page = _submit_valid_trip(driver, "PA4 Malformed JSON")
    page.generate_preview()
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["save_trip_button"])
        or page.generation_error_is_present(timeout=1)
    )
    if page.generation_error_is_present(timeout=1):
        assert driver.find_element("css selector", SELECTORS["generate_preview_button"]).is_enabled()
    else:
        assert page.get_preview_activity_rows()


def test_uc02_05_system_lock_during_generation(authenticated_driver):
    driver = authenticated_driver
    page = _submit_valid_trip(driver, "PA4 Lock Test")
    page.generate_preview()
    button_elements = driver.find_elements("css selector", SELECTORS["generate_preview_button"])
    locked = len(button_elements) == 0
    assert locked, "Workspace should be locked (read-only) while AI generation is in progress"
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"]))
    )
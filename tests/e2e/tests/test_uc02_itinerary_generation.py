"""Browser-level PA4 tests for UC02 - AI Itinerary Generation."""

import os
import sys
from uuid import uuid4

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import AI_TIMEOUT, SELECTORS
from pages.trip_creation_page import TripCreationPage


def _create_trip_and_wait_for_itinerary(driver):
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(
        destination=f"PA4 Hoi An {uuid4().hex[:6]}",
        start_date="2026-09-01",
        end_date="2026-09-03",
        capacity="3",
        budget="2500000",
        style="Balanced",
    )
    page.submit()
    page.generate_preview()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"])))
    page.save_trip()
    page.open_saved_trip()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_view"])))
    return page


def test_uc02_01_itinerary_is_generated_after_trip_creation(authenticated_driver):
    driver = authenticated_driver
    _create_trip_and_wait_for_itinerary(driver)
    assert driver.find_elements("css selector", SELECTORS["activity_row"])


def test_uc02_02_generated_itinerary_persists_after_reload(authenticated_driver):
    driver = authenticated_driver
    _create_trip_and_wait_for_itinerary(driver)
    before = len(driver.find_elements("css selector", SELECTORS["activity_row"]))
    driver.refresh()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_view"])))
    assert len(driver.find_elements("css selector", SELECTORS["activity_row"])) == before


def test_uc02_03_generated_days_and_activities_are_visible(authenticated_driver):
    driver = authenticated_driver
    _create_trip_and_wait_for_itinerary(driver)
    assert len(driver.find_elements("css selector", ".day-card")) >= 1
    assert all(row.text.strip() for row in driver.find_elements("css selector", SELECTORS["activity_row"]))


def test_uc02_04_regenerate_keeps_the_workspace_available(authenticated_driver):
    driver = authenticated_driver
    _create_trip_and_wait_for_itinerary(driver)
    driver.find_element("css selector", SELECTORS["regenerate_button"]).click()
    WebDriverWait(driver, AI_TIMEOUT).until(lambda current: not current.find_element("css selector", SELECTORS["regenerate_button"]).is_enabled())
    WebDriverWait(driver, AI_TIMEOUT).until(lambda current: current.find_element("css selector", SELECTORS["regenerate_button"]).is_enabled())
    assert driver.find_elements("css selector", SELECTORS["activity_row"])

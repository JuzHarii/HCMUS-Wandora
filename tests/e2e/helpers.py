"""
helpers.py
-----------
Small helpers shared across the UC03+ browser test files, so each one
doesn't have to re-implement "create and save a trip, then land on its
itinerary workspace" (the shared precondition for UC03-UC11, UC14, UC15).
"""

from uuid import uuid4

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.trip_creation_page import TripCreationPage
from pages.itinerary_page import ItineraryPage


def create_saved_trip(driver, destination_prefix="PA4 Trip", **overrides):
    """Runs UC01 (create) -> UC02 (generate) -> UC13 (save), and lands on
    the saved trip's itinerary workspace (UC03/UC04/UC07.../UC15's shared
    precondition). Returns an ItineraryPage for the now-open workspace.

    `overrides` lets a test override any fill_trip_form() field, e.g.
    create_saved_trip(driver, start_date="2026-01-10", end_date="2026-01-15")
    for UC07's weather-aware packing test.
    """
    fields = dict(
        destination=f"{destination_prefix} {uuid4().hex[:6]}",
        start_date="2026-09-01",
        end_date="2026-09-03",
        capacity="3",
        budget="2500000",
        style="Balanced",
    )
    fields.update(overrides)

    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(**fields)
    page.submit()
    page.generate_preview()
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["save_trip_button"]))
    )
    page.save_trip()
    page.open_saved_trip()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.url_contains("/trips/"))
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_view"]))
    )
    return ItineraryPage(driver)


def join_trip_via_invite(second_driver, invite_link):
    """Second/third driver session accepts an invite link and lands on the
    same trip's workspace."""
    second_driver.get(invite_link)
    WebDriverWait(second_driver, AI_TIMEOUT).until(EC.url_contains("/trips/"))
    WebDriverWait(second_driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_view"]))
    )
    return ItineraryPage(second_driver)
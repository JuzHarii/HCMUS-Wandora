"""Browser-level PA4 tests for UC17 - Trip History."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, BASE_URL, SELECTORS
from pages.dashboard_page import DashboardPage
from pages.members_page import MembersPage
from helpers import create_saved_trip, join_trip_via_invite


def test_uc17_01_review_and_open_saved_trips(authenticated_driver):
    """TC_UC17_01 - Review and Open Saved Trips (Basic Flow)."""
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 UC17 History")

    driver.get(f"{BASE_URL}/home")
    dashboard = DashboardPage(driver).open_history()

    cards_text = dashboard.get_trip_cards_text()
    assert cards_text, "At least the trip just created should be listed"

    dashboard.open_trip_card(index=0)
    WebDriverWait(driver, AI_TIMEOUT).until(EC.url_contains("/trips/"))


def test_uc17_02_restore_prior_itinerary_version(authenticated_driver):
    """TC_UC17_02 - Restore Prior Itinerary Version (Success Path)."""
    driver = authenticated_driver
    itinerary = create_saved_trip(driver, destination_prefix="PA4 UC17 Version")

    # Create at least one prior version via an accepted AI adjustment
    # (UC03 TC01), so Version History has something to restore.
    itinerary.request_adjustment("Replace the museum on Day 2 with an outdoor activity.")
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["itinerary_adjustment_preview"])
    )
    itinerary.accept_adjustment()
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: not d.find_elements("css selector", SELECTORS["itinerary_adjustment_preview"])
    )

    dashboard = DashboardPage(driver)
    dashboard.open_version_history()
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["version_history_item"])
    )
    dashboard.restore_version(version_index=0)

    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_view"]))
    )


def test_uc17_03_empty_history_placeholder(authenticated_driver):
    """TC_UC17_03 - Empty History Placeholder (Alternative Flow 1)."""
    driver = authenticated_driver
    dashboard = DashboardPage(driver).open_history()

    empty_text = dashboard.get_empty_history_text().lower()
    assert "no trips yet" in empty_text
    assert dashboard.is_present(SELECTORS["trip_invitation_continue"], timeout=3) or dashboard.is_present(
        "[data-testid='create-new-trip-button']", timeout=3
    )


def test_uc17_04_new_trip_no_previous_versions(authenticated_driver):
    """TC_UC17_04 - New Trip - No Previous Versions (Alternative Flow 2)."""
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 UC17 No Versions")

    dashboard = DashboardPage(driver)
    dashboard.open_version_history()

    empty_text = dashboard.get_version_history_empty_text().lower()
    assert "no previous versions" in empty_text


def test_uc17_05_viewer_prevented_from_restoring_versions(authenticated_driver, second_authenticated_driver):
    """TC_UC17_05 - Viewer Prevented from Restoring Versions (RBAC Check)."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 UC17 Viewer RBAC")

    owner_page.request_adjustment("Add afternoon tea to Day 3.")
    WebDriverWait(owner_driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["itinerary_adjustment_preview"])
    )
    owner_page.accept_adjustment()

    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    join_trip_via_invite(second_authenticated_driver, invite_link)

    dashboard_viewer = DashboardPage(second_authenticated_driver)
    dashboard_viewer.open_version_history()
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["version_history_item"])
    )
    assert not dashboard_viewer.restore_button_is_present(timeout=3), (
        "Restore control must be disabled or hidden for Viewers"
    )
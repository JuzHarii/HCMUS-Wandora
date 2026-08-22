"""Browser-level PA4 tests for UC04 - Manual Places and External Links."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.members_page import MembersPage
from helpers import create_saved_trip, join_trip_via_invite


def test_uc04_01_successfully_add_custom_place(authenticated_driver):
    """TC_UC04_01 - Successfully Add Custom Place (Basic Flow)."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Paris")

    page.open_add_activity_form()
    page.fill_activity_form(
        name="Louvre Museum",
        category="Sightseeing",
        notes="Morning tickets booked",
        url="https://www.louvre.fr",
    )
    page.save_activity()

    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: any("Louvre Museum" in row.text for row in d.find_elements("css selector", SELECTORS["activity_row"]))
    )
    assert page.is_present(SELECTORS["activity_manual_badge"], timeout=5), (
        "Manually added activities must render with the manual/map badge"
    )


def test_uc04_02_invalid_url_format_blocks_submission(authenticated_driver):
    """TC_UC04_02 - Add Activity Fails - Invalid URL Format (Alternative Flow 1)."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Paris")

    page.open_add_activity_form()
    page.fill_activity_form(
        name="Louvre Museum",
        category="Sightseeing",
        url="broken_link_with_no_http_or_domain",
    )
    page.save_activity()

    assert "valid url" in page.get_activity_validation_text().lower()


def test_uc04_03_viewer_add_activity_controls_are_hidden(authenticated_driver, second_authenticated_driver):
    """TC_UC04_03 - Custom Place Addition - Missing Mandatory Name.

    NOTE: the xlsx template's Case ID/title for TC_UC04_03 says "Missing
    Mandatory Name" but its actual steps/expected-result describe a
    Viewer being unable to reach the Add Activity controls at all (that
    scenario is what's implemented below). See TC_UC04_04 for the real
    missing-name validation case.
    """
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 Hanoi")

    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    viewer_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    assert not viewer_page.add_activity_control_is_visible(timeout=3), (
        "Add Activity / Place controls must be completely disabled or hidden for Viewers"
    )


def test_uc04_04_add_custom_place_missing_mandatory_name(authenticated_driver):
    """TC_UC04_04 - Add Custom Place - Missing Mandatory Name."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Hanoi")

    page.open_add_activity_form()
    page.fill_activity_form(notes="Just some notes, no name given")
    page.save_activity()

    assert "place name is required" in page.get_activity_validation_text().lower()


def test_uc04_05_extreme_input_text_length_boundary_check(authenticated_driver):
    """TC_UC04_05 - Extreme Input Text Length Boundary Check on Notes."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Hanoi")
    long_notes = "A" * 1500

    page.open_add_activity_form()
    page.fill_activity_form(name="Extreme Notes Stop", category="Sightseeing", notes=long_notes)
    page.save_activity()

    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: any("Extreme Notes Stop" in row.text for row in d.find_elements("css selector", SELECTORS["activity_row"]))
    )
    driver.refresh()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_view"])))
    saved_row = next(
        row for row in driver.find_elements("css selector", SELECTORS["activity_row"])
        if "Extreme Notes Stop" in row.text
    )
    assert long_notes[:50] in saved_row.text, "Notes must persist without truncation"
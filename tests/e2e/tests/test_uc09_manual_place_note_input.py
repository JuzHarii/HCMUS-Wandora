"""Browser-level PA4 tests for UC09 - Manual Place Note Input."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.members_page import MembersPage
from helpers import create_saved_trip, join_trip_via_invite


def test_uc09_01_successful_itinerary_activity_note_update(authenticated_driver):
    """TC_UC09_01 - Successful Itinerary Activity Note Update (Basic Flow)."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Eiffel Tower")

    page.edit_notes(activity_index=0)
    page.set_note_text("Eiffel Tower sunset slot booked for 6:30 PM.")
    page.save_notes()

    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: "sunset slot booked" in d.find_elements("css selector", SELECTORS["activity_row"])[0].text.lower()
    )


def test_uc09_02_viewer_note_edit_restriction(authenticated_driver, second_authenticated_driver):
    """TC_UC09_02 - Viewer Note Edit Restriction (Alternative Flow 1)."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Rome")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    viewer_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    assert not viewer_page.edit_notes_control_is_visible(activity_index=0, timeout=3), (
        "Edit Notes action must be hidden or disabled for Viewers"
    )

    status = second_authenticated_driver.execute_async_script(
        """
        const callback = arguments[arguments.length - 1];
        fetch('/api/v1/activities/notes', {
            method: 'PATCH', credentials: 'include',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({note: 'direct api attempt'}),
        }).then(r => callback(r.status)).catch(() => callback(-1));
        """
    )
    assert status == 403


def test_uc09_03_empty_note_clear_and_persist(authenticated_driver):
    """TC_UC09_03 - Empty Note Clear and Persist."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Madrid")

    page.edit_notes(activity_index=0)
    page.set_note_text("A note that will later be cleared.")
    page.save_notes()
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: "cleared" in d.find_elements("css selector", SELECTORS["activity_row"])[0].text.lower()
    )

    page.edit_notes(activity_index=0)
    page.set_note_text("", clear_first=True)
    page.save_notes()

    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: "cleared" not in d.find_elements("css selector", SELECTORS["activity_row"])[0].text.lower()
    )


def test_uc09_04_long_character_text_input_check(authenticated_driver):
    """TC_UC09_04 - Long Character Text Input Check."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Amsterdam")
    long_text = "B" * 2000

    page.edit_notes(activity_index=0)
    page.set_note_text(long_text)
    page.save_notes()

    driver.refresh()
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["itinerary_view"])
    )
    row_text = driver.find_elements("css selector", SELECTORS["activity_row"])[0].text
    assert long_text[:50] in row_text


def test_uc09_05_simultaneous_editing_concurrency_check(authenticated_driver, second_authenticated_driver):
    """TC_UC09_05 - Simultaneous Editing Concurrency Check."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 Eiffel Tower Concurrency")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    editor_b_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    owner_page.edit_notes(activity_index=0)

    editor_b_page.edit_notes(activity_index=0)
    lock_text = editor_b_page.get_notes_locked_text().lower()
    assert "currently being edited" in lock_text
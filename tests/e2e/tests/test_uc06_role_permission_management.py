"""Browser-level PA4 tests for UC06 - Role and Permission Management."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT
from pages.members_page import MembersPage
from helpers import create_saved_trip, join_trip_via_invite


def _owner_with_one_member(owner_driver, other_driver, role):
    create_saved_trip(owner_driver, destination_prefix="PA4 Bali")
    invite_link = MembersPage(owner_driver).invite(other_driver.pa4_email, role).get_invite_link()
    join_trip_via_invite(other_driver, invite_link)
    return MembersPage(owner_driver)


def test_uc06_01_successful_role_update(authenticated_driver, second_authenticated_driver):
    """TC_UC06_01 - Successful Role Update (Basic Flow)."""
    owner_driver = authenticated_driver
    members = _owner_with_one_member(owner_driver, second_authenticated_driver, "Editor")

    members.set_member_role(member_index=0, new_role="Viewer")

    # User_A's session should dynamically lose editing privileges without
    # a manual reload (pushed over websocket).
    from pages.itinerary_page import ItineraryPage
    editor_becoming_viewer = ItineraryPage(second_authenticated_driver)
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: editor_becoming_viewer.adjustment_input_is_locked(timeout=2)
    )


def test_uc06_02_viewer_action_modification_attempt(authenticated_driver, second_authenticated_driver):
    """TC_UC06_02 - Viewer Action Modification Attempt (Alternative Flow 1)."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Phuket")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    viewer_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    assert not viewer_page.add_activity_control_is_visible(timeout=3)
    assert viewer_page.adjustment_input_is_locked(timeout=3)


def test_uc06_03_trip_ownership_transfer_flow(authenticated_driver, second_authenticated_driver):
    """TC_UC06_03 - Trip Ownership Transfer Flow."""
    owner_driver = authenticated_driver
    members = _owner_with_one_member(owner_driver, second_authenticated_driver, "Editor")

    members.set_member_role(member_index=0, new_role="Owner")
    members.confirm_ownership_transfer()

    rows_text = " ".join(members.get_member_rows_text())
    assert "editor" in rows_text.lower(), "Previous Owner must be automatically demoted to Editor"


def test_uc06_04_direct_api_endpoint_rbac_enforcement(authenticated_driver, second_authenticated_driver):
    """TC_UC06_04 - Direct API Endpoint RBAC Enforcement (Security Bypass).

    Selenium can't run Postman, but it can drive the browser's own fetch()
    to reproduce "capture and dispatch a POST request directly" against
    the itineraries endpoint while authenticated as a Viewer, and assert
    the backend rejects it with 403 regardless of what the UI shows.
    """
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Danang")
    trip_id = owner_driver.current_url.rstrip("/").split("/")[-1]

    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    join_trip_via_invite(second_authenticated_driver, invite_link)

    status = second_authenticated_driver.execute_async_script(
        """
        const callback = arguments[arguments.length - 1];
        fetch('/api/v1/itineraries/' + arguments[0], {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({activities: []}),
        }).then(r => callback(r.status)).catch(() => callback(-1));
        """,
        trip_id,
    )
    assert status == 403


def test_uc06_05_demote_last_owner_protection_check(authenticated_driver):
    """TC_UC06_05 - Demote Last Owner Protection Check."""
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 Vientiane")

    members = MembersPage(driver).open_modal()
    if members.self_role_select_is_disabled(member_index=0):
        return

    members.set_member_role(member_index=0, new_role="Editor")
    error_text = members.get_demote_last_owner_error_text().lower()
    assert "at least one active owner" in error_text
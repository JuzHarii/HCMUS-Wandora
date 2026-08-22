"""Browser-level PA4 tests for UC05 - Group Collaboration."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.members_page import MembersPage
from helpers import create_saved_trip, join_trip_via_invite


def test_uc05_01_successful_invite_link_dispatch(authenticated_driver, second_authenticated_driver):
    """TC_UC05_01 - Successful Invite Link Dispatch (Basic Flow)."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Bangkok")

    members = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor")
    invite_link = members.get_invite_link()

    assert invite_link, "A shareable invite link must be produced"
    rows_text = " ".join(members.get_member_rows_text())
    assert "pending" in rows_text.lower() and "editor" in rows_text.lower()


def test_uc05_02_invitee_successfully_joins_trip(authenticated_driver, second_authenticated_driver):
    """TC_UC05_02 - Invitee Successfully Joins Trip (Success Path)."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Seoul")

    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    join_trip_via_invite(second_authenticated_driver, invite_link)

    assert "/trips/" in second_authenticated_driver.current_url


def test_uc05_03_editor_viewer_administrative_lock(authenticated_driver, second_authenticated_driver):
    """TC_UC05_03 - Editor / Viewer Administrative Lock (Alternative Flow 1)."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Osaka")

    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    join_trip_via_invite(second_authenticated_driver, invite_link)

    members_as_viewer = MembersPage(second_authenticated_driver)
    assert not members_as_viewer.invite_controls_are_visible(timeout=3), (
        "Invite/role administration controls must be hidden for non-Owners"
    )


def test_uc05_04_duplicate_member_invitation_prevention(authenticated_driver, second_authenticated_driver):
    """TC_UC05_04 - Duplicate Member Invitation Prevention (Alternative Flow 2)."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Kyoto")

    members = MembersPage(owner_driver)
    members.invite(second_authenticated_driver.pa4_email, "Editor")

    # Re-open the modal and try inviting the same (now-member) email again.
    members.invite(second_authenticated_driver.pa4_email, "Editor")
    warning = members.get_duplicate_invite_warning_text().lower()
    assert "already a member" in warning


def test_uc05_05_expired_or_malformed_invitation_token(authenticated_driver):
    """TC_UC05_05 - Expired or Malformed Invitation Token Access."""
    driver = authenticated_driver
    from config import BASE_URL

    driver.get(f"{BASE_URL}/invite/expired-or-malformed-token-000000")
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["invite_invalid_token_warning"])
        or "auth" in d.current_url
    )
    assert MembersPage(driver).get_invalid_token_warning_text()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.url_contains("/auth"))
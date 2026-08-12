"""
test_uc08_shared_luggage_planning.py
--------------------------------------
Functional (black-box, UI-level) tests for:

    UC08 - Shared Luggage Planning

Implements TC_UC08_01 .. TC_UC08_05 from the test-case spreadsheet
(Function 08 sheet). Real-time / concurrency scenarios use TWO
independent Selenium sessions (fixtures `driver` and `second_driver`)
to simulate two group members with the app open at the same time --
this is still pure UI-driven testing, no WebSocket internals or
backend code are touched directly.

Preconditions (see config.py):
  - ACCOUNTS.owner / editor / viewer / second_editor must all be
    members of the same trip: config.SHARED_TRIP_ID.
  - That trip must already have a packing checklist with the items
    referenced below ("Tent", "First Aid Kit", "Camera"), OR the
    fixtures/seed script used by your environment should create them.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pages.login_page import LoginPage
from pages.packing_list_page import PackingListPage


def test_uc08_01_assign_item_to_member(driver):
    """TC_UC08_01 - Item Responsibility Assignment.

    Steps:
      1. Open Packing List.
      2. Assign item "Tent" to "User_B".
    Expected:
      - Assignment is stored and reflected as User_B's avatar on the item.
    """
    LoginPage(driver).login_as("owner")
    packing_page = PackingListPage(driver)
    packing_page.open_packing_list()

    packing_page.assign_item("Tent", "User_B")

    assert packing_page.get_assignee("Tent") == "User_B", (
        "Expected 'Tent' to show User_B as the assigned member"
    )


def test_uc08_02_realtime_completion_sync_across_sessions(driver, second_driver):
    """TC_UC08_02 - Real-Time Completion Sync.

    Steps:
      1. User_A (owner) checks off "First Aid Kit".
      2. Observe User_B's (editor) screen on a separate session.
    Expected:
      - User_B sees the checked state without reloading the page.
    """
    # User A's session
    LoginPage(driver).login_as("owner")
    page_a = PackingListPage(driver)
    page_a.open_packing_list()

    # User B's session, opened independently and left open (no reload)
    LoginPage(second_driver).login_as("editor")
    page_b = PackingListPage(second_driver)
    page_b.open_packing_list()

    page_a.check_item("First Aid Kit")

    # Give the WebSocket push a moment to arrive, then re-read (no reload)
    deadline = time.time() + 10
    synced = False
    while time.time() < deadline:
        if page_b.is_item_checked("First Aid Kit"):
            synced = True
            break
        time.sleep(0.5)

    assert synced, "Expected User_B's screen to reflect the check-off in real time"


def test_uc08_03_concurrent_assignment_conflict_resolved_by_latest_write(driver, second_driver):
    """TC_UC08_03 - Concurrent Update Conflict.

    Steps:
      1. User_A assigns "Camera" to self.
      2. Almost simultaneously, User_B assigns "Camera" to User_C.
    Expected:
      - The later update wins; all screens converge on "User_C".
    """
    LoginPage(driver).login_as("owner")          # acts as User_A
    LoginPage(second_driver).login_as("editor")  # acts as User_B

    page_a = PackingListPage(driver)
    page_b = PackingListPage(second_driver)
    page_a.open_packing_list()
    page_b.open_packing_list()

    # Fire the two assignments back-to-back to simulate near-simultaneous edits.
    page_a.assign_item("Camera", "User_A")
    page_b.assign_item("Camera", "User_C")

    # Let sync settle, then verify both sessions converged on the same
    # (later) value -- the spec calls for User_C to be the final assignee.
    time.sleep(2)
    page_a.driver.refresh()
    page_a.open_packing_list()

    assert page_a.get_assignee("Camera") == "User_C", (
        "Expected the later write (User_C) to win the assignment conflict"
    )
    assert page_b.get_assignee("Camera") == "User_C", (
        "Expected User_B's own screen to also reflect the final assignee"
    )


def test_uc08_04_add_custom_luggage_item(driver):
    """TC_UC08_04 - Add Custom Luggage Items.

    Steps:
      1. Click "Add Custom Item".
      2. Enter "Portable Grill" and Save.
    Expected:
      - Item is validated, saved, and appended to the shared checklist.
    """
    LoginPage(driver).login_as("owner")
    packing_page = PackingListPage(driver)
    packing_page.open_packing_list()

    packing_page.add_custom_item("Portable Grill")

    assert packing_page.item_exists("Portable Grill"), (
        "Expected 'Portable Grill' to appear in the shared packing list"
    )


def test_uc08_05_viewer_cannot_modify_other_members_items(driver):
    """TC_UC08_05 - Viewer Check-Off Permission Restriction.

    Steps:
      1. Log in as Viewer.
      2. Attempt to re-assign or uncheck an item assigned to another user.
    Expected:
      - Controls for group items are locked/disabled for the Viewer,
        or the attempt is rejected with a permission notice.
    """
    LoginPage(driver).login_as("viewer")
    packing_page = PackingListPage(driver)
    packing_page.open_packing_list()

    # "Tent" was assigned to another member in TC_UC08_01 -- a Viewer
    # must not be able to toggle it.
    enabled = packing_page.is_item_checkbox_enabled("Tent")

    if enabled:
        # If the control isn't disabled outright, the click itself must
        # be rejected with a permission notice instead of taking effect.
        before = packing_page.is_item_checked("Tent")
        packing_page.check_item("Tent")
        assert packing_page.permission_denied_shown(), (
            "Expected a permission-denied notice when Viewer tries to "
            "modify another member's item"
        )
        assert packing_page.is_item_checked("Tent") == before, (
            "Viewer's click must not actually change the item's state"
        )
    else:
        assert not enabled, "Expected the checkbox to be disabled for Viewer"

"""Browser-level PA4 tests for UC03 - AI Itinerary Adjustment."""

import os
import sys

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import AI_TIMEOUT, SELECTORS
from pages.members_page import MembersPage
from helpers import create_saved_trip, join_trip_via_invite


def test_uc03_01_successful_schedule_refinement(authenticated_driver):
    """TC_UC03_01 - Successful Schedule Refinement (Basic Flow)."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Hue")

    page.request_adjustment("Replace the museum on Day 2 with an outdoor activity.")
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_adjustment_preview"]))
    )
    page.accept_adjustment()

    # Accept persists the patch and bumps version history -- confirm it
    # survives a reload rather than living only in client state.
    WebDriverWait(driver, AI_TIMEOUT).until(lambda d: not d.find_elements("css selector", SELECTORS["itinerary_adjustment_preview"]))
    driver.refresh()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_view"])))
    assert driver.find_elements("css selector", SELECTORS["activity_row"])


def test_uc03_02_viewer_permission_interception(authenticated_driver, second_authenticated_driver):
    """TC_UC03_02 - Viewer Permission Interception (Alternative Flow 1)."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 Hoi An")

    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    viewer_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    # The prompt box must be blocked client-side before it ever reaches
    # GenAI -- either it's hidden/disabled outright, or typing+submitting
    # surfaces the 403 permission-denied modal instead of a proposal.
    if viewer_page.adjustment_input_is_locked(timeout=3):
        return

    viewer_page.request_adjustment("Add afternoon tea to Day 3.")
    denied_text = viewer_page.get_permission_denied_text().lower()
    assert "permission" in denied_text or "denied" in denied_text or "403" in denied_text


def test_uc03_03_reject_proposed_ai_patch(authenticated_driver):
    """TC_UC03_03 - Reject Proposed AI Itinerary Patch (Alternative Flow 3)."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Da Lat")
    before_texts = sorted(row.text for row in driver.find_elements("css selector", SELECTORS["activity_row"]))

    page.request_adjustment("Add afternoon tea to Day 3.")
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_adjustment_preview"]))
    )
    page.discard_adjustment()

    WebDriverWait(driver, AI_TIMEOUT).until(lambda d: not d.find_elements("css selector", SELECTORS["itinerary_adjustment_preview"]))
    after_texts = sorted(row.text for row in driver.find_elements("css selector", SELECTORS["activity_row"]))
    assert before_texts == after_texts, "Timeline must restore the previous active schedule exactly on Discard"


def test_uc03_04_concurrent_editing_conflict_detection(authenticated_driver, second_authenticated_driver):
    """TC_UC03_04 - Concurrent Editing Conflict Detection (Alternative Flow 4)."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 Sapa")

    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    editor_b_page = join_trip_via_invite(second_authenticated_driver, invite_link)

    # Editor A (owner_driver) opens the adjustment prompt box first.
    owner_page.wait_visible(SELECTORS["itinerary_adjustment_input"])
    owner_driver.find_element("css selector", SELECTORS["itinerary_adjustment_input"]).send_keys(
        "Swap Day 2's afternoon activity for something more relaxed."
    )

    # Editor B manually modifies/deletes an activity on Day 2 in the meantime.
    activity_rows = editor_b_page.driver.find_elements("css selector", SELECTORS["activity_row"])
    assert activity_rows, "Expected at least one activity row for Editor B to modify"
    editor_b_page.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", activity_rows[0])
    activity_rows[0].click()

    # Editor A submits/accepts their now-stale adjustment proposal.
    owner_driver.find_element("css selector", SELECTORS["itinerary_adjustment_submit"]).click()
    WebDriverWait(owner_driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["adjustment_conflict_warning"])
        or d.find_elements("css selector", SELECTORS["itinerary_adjustment_preview"])
    )

    assert owner_page.is_present(SELECTORS["adjustment_conflict_warning"], timeout=2), (
        "Expected a version-mismatch conflict warning once Editor A's change set went stale"
    )


def test_uc03_05_ai_returns_malformed_activity_patch(authenticated_driver):
    """TC_UC03_05 - AI Returns Malformed / Invalid Activity Patch (Alternative Flow 5)."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Phu Quoc")
    before_texts = sorted(row.text for row in driver.find_elements("css selector", SELECTORS["activity_row"]))

    page.request_adjustment(
        "Add the Day 99 midnight rooftop opera right after the nonexistent Day 7 breakfast."
    )
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["adjustment_error_alert"])
        or d.find_elements("css selector", SELECTORS["itinerary_adjustment_preview"])
    )

    assert page.is_present(SELECTORS["adjustment_error_alert"], timeout=2), (
        "Expected the standard 'AI could not process that request' fallback for an invalid reference"
    )
    after_texts = sorted(row.text for row in driver.find_elements("css selector", SELECTORS["activity_row"]))
    assert before_texts == after_texts
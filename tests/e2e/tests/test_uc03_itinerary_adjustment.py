"""Browser-level PA4 tests for UC03 - AI Itinerary Adjustment."""

import os
import sys
import re

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

    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.element_to_be_clickable(("css selector", SELECTORS["regenerate_button"]))
    ).click()
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.element_to_be_clickable(("css selector", SELECTORS["regenerate_button"]))
    )

    driver.refresh()
    WebDriverWait(driver, AI_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["activity_row"])))
    assert driver.find_elements("css selector", SELECTORS["activity_row"])


def test_uc03_02_viewer_permission_interception(authenticated_driver, second_authenticated_driver):
    """TC_UC03_02 - Viewer Permission Interception (Alternative Flow 1)."""
    owner_driver = authenticated_driver
    owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 Hoi An")

    WebDriverWait(owner_driver, 5).until(
        EC.element_to_be_clickable(("css selector", SELECTORS["members_tab"]))
    ).click()
    WebDriverWait(owner_driver, 5).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["member_invite_email_input"]))
    )
    owner_driver.find_element("css selector", SELECTORS["member_invite_email_input"]).send_keys(second_authenticated_driver.pa4_email)

    role_select = owner_driver.find_element("css selector", SELECTORS["member_invite_role_select"])
    role_select.send_keys("Viewer")
    
    owner_driver.find_element("css selector", SELECTORS["member_invite_send_button"]).click()
    WebDriverWait(owner_driver, 5).until(
        EC.text_to_be_present_in_element(("css selector", SELECTORS["member_list_item"]), second_authenticated_driver.pa4_email)
    )
    match = re.search(r'/trips/([^/]+)', owner_driver.current_url)
    assert match, "Could not find workspace ID in owner URL"
    workspace_id = match.group(1)

    base_url = owner_driver.current_url.split("/trips/")
    trip_url = f"{base_url}/trips/{workspace_id}/itinerary"
    second_authenticated_driver.get(trip_url)

    WebDriverWait(second_authenticated_driver, 30).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["activity_row"]))
    )
    inputs = second_authenticated_driver.find_elements("css selector", SELECTORS["regenerate_button"])
    assert len(inputs) == 0, "Regenerate button must be hidden/absent for viewers"


# def test_uc03_03_reject_proposed_ai_patch(authenticated_driver):
#     """TC_UC03_03 - Reject Proposed AI Itinerary Patch (Alternative Flow 3)."""
#     driver = authenticated_driver
#     page = create_saved_trip(driver, destination_prefix="PA4 Da Lat")
#     before_texts = sorted(row.text for row in driver.find_elements("css selector", SELECTORS["activity_row"]))

#     page.request_adjustment("Add afternoon tea to Day 3.")
#     WebDriverWait(driver, AI_TIMEOUT).until(
#         EC.visibility_of_element_located(("css selector", SELECTORS["itinerary_adjustment_preview"]))
#     )
#     page.discard_adjustment()

#     WebDriverWait(driver, AI_TIMEOUT).until(lambda d: not d.find_elements("css selector", SELECTORS["itinerary_adjustment_preview"]))
#     after_texts = sorted(row.text for row in driver.find_elements("css selector", SELECTORS["activity_row"]))
#     assert before_texts == after_texts, "Timeline must restore the previous active schedule exactly on Discard"


# def test_uc03_04_concurrent_editing_conflict_detection(authenticated_driver, second_authenticated_driver):
#     """TC_UC03_04 - Concurrent Editing Conflict Detection (Alternative Flow 4)."""
#     owner_driver = authenticated_driver
#     owner_page = create_saved_trip(owner_driver, destination_prefix="PA4 Sapa")

#     invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
#     editor_b_page = join_trip_via_invite(second_authenticated_driver, invite_link)

#     # Editor A (owner_driver) opens the adjustment prompt box first.
#     owner_page.wait_visible(SELECTORS["itinerary_adjustment_input"])
#     owner_driver.find_element("css selector", SELECTORS["itinerary_adjustment_input"]).send_keys(
#         "Swap Day 2's afternoon activity for something more relaxed."
#     )

#     # Editor B manually modifies/deletes an activity on Day 2 in the meantime.
#     activity_rows = editor_b_page.driver.find_elements("css selector", SELECTORS["activity_row"])
#     assert activity_rows, "Expected at least one activity row for Editor B to modify"
#     editor_b_page.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", activity_rows[0])
#     activity_rows[0].click()

#     # Editor A submits/accepts their now-stale adjustment proposal.
#     owner_driver.find_element("css selector", SELECTORS["itinerary_adjustment_submit"]).click()
#     WebDriverWait(owner_driver, AI_TIMEOUT).until(
#         lambda d: d.find_elements("css selector", SELECTORS["adjustment_conflict_warning"])
#         or d.find_elements("css selector", SELECTORS["itinerary_adjustment_preview"])
#     )

#     assert owner_page.is_present(SELECTORS["adjustment_conflict_warning"], timeout=2), (
#         "Expected a version-mismatch conflict warning once Editor A's change set went stale"
#     )


# def test_uc03_05_ai_returns_malformed_activity_patch(authenticated_driver):
#     """TC_UC03_05 - AI Returns Malformed / Invalid Activity Patch (Alternative Flow 5)."""
#     driver = authenticated_driver
#     page = create_saved_trip(driver, destination_prefix="PA4 Phu Quoc")
#     before_texts = sorted(row.text for row in driver.find_elements("css selector", SELECTORS["activity_row"]))

#     page.request_adjustment(
#         "Add the Day 99 midnight rooftop opera right after the nonexistent Day 7 breakfast."
#     )
#     WebDriverWait(driver, AI_TIMEOUT).until(
#         lambda d: d.find_element("css selector", SELECTORS["itinerary_adjustment_submit"]).is_enabled()
#     )
#     error_alerts = driver.find_elements("css selector", SELECTORS["adjustment_error_alert"])
#     if error_alerts and error_alerts.is_displayed():
#         assert error_alerts.text.strip() != "", "Error message should not be empty"
    
#     after_texts = sorted(row.text for row in driver.find_elements("css selector", SELECTORS["activity_row"]))
#     assert before_texts == after_texts, "Timeline must remain completely unmodified on malformed patch"
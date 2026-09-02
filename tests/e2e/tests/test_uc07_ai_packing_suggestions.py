"""Browser-level PA4 tests for UC07 - AI Packing Suggestions."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.packing_page import PackingPage
from helpers import create_saved_trip


def test_uc07_01_weather_aware_suggestions_generation(authenticated_driver):
    """TC_UC07_01 - Weather-Aware Suggestions Generation (Basic Flow)."""
    driver = authenticated_driver
    create_saved_trip(
        driver,
        destination_prefix="PA4 Sapporo Japan",
        start_date="2027-01-10",
        end_date="2027-01-15",
    )
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.invisibility_of_element_located(("css selector", SELECTORS["workspace_loading"]))
    )
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.element_to_be_clickable(("css selector", SELECTORS["packing_tab"]))
    ).click()
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.invisibility_of_element_located(("css selector", SELECTORS["workspace_loading"]))
    )
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.element_to_be_clickable(("css selector", SELECTORS["generate_packing_button"]))
    ).click()
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.invisibility_of_element_located(("css selector", SELECTORS["workspace_loading"]))
    )

    items = driver.find_elements("css selector", SELECTORS["packing_item_row"]) or driver.find_elements("css selector", ".packing-list li")
    items_text = " ".join(item.text for item in items).lower()
    assert any(word in items_text for word in ["boot", "coat", "thermal", "jacket", "glove", "warm"]), (
        f"Winter-destination checklist should surface cold-weather items. Current list: {items_text}"
    )


# def test_uc07_02_ai_connection_outage_fallback_to_standard_template(authenticated_driver):
#     """TC_UC07_02 - AI Connection Outage - Falling Back to Standard Template (Alternative Flow 1)."""
#     driver = authenticated_driver
#     create_saved_trip(driver, destination_prefix="PA4 Reykjavik")

#     packing = PackingPage(driver).open_tab()
#     packing.generate_checklist()

#     # No network mocking layer exists in this suite (it runs against the
#     # real backend end-to-end), so this asserts the fallback contract:
#     # *either* a live AI checklist renders, *or*, if the AI call fails,
#     # the offline warning + a static template must render instead of a
#     # blank/broken screen.
#     WebDriverWait(driver, AI_TIMEOUT).until(
#         lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"])
#         or d.find_elements("css selector", SELECTORS["packing_offline_warning"])
#     )
#     if packing.is_present(SELECTORS["packing_offline_warning"], timeout=2):
#         assert "offline" in packing.get_offline_warning_text().lower()
#         assert packing.get_packing_items_text(), "A static template checklist must still be populated"
#     else:
#         assert packing.get_packing_items_text()


def test_uc07_03_activity_based_suggestions_tag_extraction(authenticated_driver):
    """TC_UC07_03 - Activity-Based Suggestions Tag Extraction."""
    driver = authenticated_driver
    page = create_saved_trip(driver, destination_prefix="PA4 Sydney")

    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.invisibility_of_element_located(("css selector", SELECTORS["workspace_loading"]))
    )
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.element_to_be_clickable(("css selector", ".recovery-link"))
    ).click()
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", "form.manual-activity-form"))
    )
    driver.find_element("css selector", "form.manual-activity-form input[placeholder*='market']").send_keys("Swimming at Bondi Beach")
    driver.find_element("css selector", "form.manual-activity-form button[type='submit']").click()

    WebDriverWait(driver, 5).until(
        EC.invisibility_of_element_located(("css selector", "form.manual-activity-form"))
    )
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: any("Bondi Beach" in row.text for row in d.find_elements("css selector", SELECTORS["activity_row"]))
    )

    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.invisibility_of_element_located(("css selector", SELECTORS["workspace_loading"]))
    )
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.element_to_be_clickable(("css selector", SELECTORS["packing_tab"]))
    ).click()

    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.invisibility_of_element_located(("css selector", SELECTORS["workspace_loading"]))
    )
    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.element_to_be_clickable(("css selector", SELECTORS["generate_packing_button"]))
    ).click()

    WebDriverWait(driver, AI_TIMEOUT).until(
        EC.invisibility_of_element_located(("css selector", SELECTORS["workspace_loading"]))
    )
    items = driver.find_elements("css selector", SELECTORS["packing_item_row"]) or driver.find_elements("css selector", ".packing-list li")
    items_text = " ".join(item.text for item in items).lower()
    
    assert "swim" in items_text or "sunscreen" in items_text or "towel" in items_text, (
        "Activity-based suggestions should contain swimming-related gear like swim, towel or sunscreen"
    )


# def test_uc07_04_overwriting_existing_suggestions_flow(authenticated_driver):
#     """TC_UC07_04 - Overwriting Existing Suggestions Flow."""
#     driver = authenticated_driver
#     create_saved_trip(driver, destination_prefix="PA4 Da Nang")

#     packing = PackingPage(driver).open_tab()
#     packing.generate_checklist()
#     WebDriverWait(driver, AI_TIMEOUT).until(lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"]))

#     packing.generate_checklist()
#     packing.confirm_overwrite()
#     WebDriverWait(driver, AI_TIMEOUT).until(lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"]))
#     assert packing.get_packing_items_text()


# def test_uc07_05_missing_required_metadata_interception(authenticated_driver):
#     """TC_UC07_05 - Missing Required Metadata Interception."""
#     driver = authenticated_driver
#     itinerary = create_saved_trip(driver, destination_prefix="PA4 Blank Dates")

#     # Clear the trip's dates from the workspace settings if exposed, then
#     # attempt to generate. If date-clearing isn't exposed post-save, this
#     # falls back to asserting the warning appears whenever dates are
#     # genuinely absent on a freshly-created (not-yet-dated) trip context.
#     packing = PackingPage(driver).open_tab()
#     packing.generate_checklist()
#     WebDriverWait(driver, AI_TIMEOUT).until(
#         lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"])
#         or d.find_elements("css selector", SELECTORS["packing_missing_metadata_warning"])
#     )
#     if packing.is_present(SELECTORS["packing_missing_metadata_warning"], timeout=2):
#         assert "travel dates" in packing.get_missing_metadata_warning_text().lower()
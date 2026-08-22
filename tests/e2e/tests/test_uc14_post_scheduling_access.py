"""Browser-level PA4 tests for UC14 - Post-Scheduling Feature Access."""

import os
import sys
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.dashboard_page import DashboardPage
from pages.members_page import MembersPage
from pages.trip_creation_page import TripCreationPage
from helpers import create_saved_trip, join_trip_via_invite

POST_SCHEDULING_TABS = ("packing_tab", "reviews_tab", "share_export_tab")


def test_uc14_01_unlock_tabs_after_itinerary_acceptance(authenticated_driver):
    """TC_UC14_01 - Unlock Tabs After Itinerary Acceptance (Basic Flow)."""
    driver = authenticated_driver
    dashboard = DashboardPage(driver)
    create_saved_trip(driver, destination_prefix="PA4 UC14 Unlock")

    for tab_key in POST_SCHEDULING_TABS:
        assert dashboard.tab_is_reachable(tab_key, timeout=5), f"{tab_key} should be unlocked after saving"
        dashboard.open_tab(tab_key)


def test_uc14_02_completion_indicator_tracking(authenticated_driver):
    """TC_UC14_02 - Completion Indicator Tracking."""
    driver = authenticated_driver
    itinerary = create_saved_trip(driver, destination_prefix="PA4 UC14 Progress")
    dashboard = DashboardPage(driver)

    dashboard.open_tab("packing_tab")
    driver.find_element("css selector", SELECTORS["generate_packing_button"]).click()
    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"])
    )

    itinerary.open_add_activity_form()
    itinerary.fill_activity_form(name="External reservation link", category="Sightseeing", url="https://example.com/booking")
    itinerary.save_activity()

    driver.get(driver.current_url)  # reload back to overview
    completion_text = dashboard.get_completion_indicator_text()
    assert any(char.isdigit() for char in completion_text), "Completion indicator must show a numeric progress metric"


def test_uc14_03_access_locked_feature_before_itinerary(authenticated_driver):
    """TC_UC14_03 - Access Locked Feature Before Itinerary (Alternative Flow 1)."""
    driver = authenticated_driver
    page = TripCreationPage(driver).open_trip_creation()
    page.fill_trip_form(
        destination=f"PA4 UC14 Draft {uuid4().hex[:6]}",
        start_date="2026-09-01",
        end_date="2026-09-03",
        capacity="2",
    )
    page.submit()
    # Deliberately stop before generate_preview()/save_trip(): the trip
    # stays in Draft status with no accepted itinerary.

    dashboard = DashboardPage(driver)
    for tab_key in POST_SCHEDULING_TABS:
        if dashboard.tab_is_reachable(tab_key, timeout=2):
            dashboard.open_tab(tab_key)
            assert "generate or accept" in dashboard.get_feature_locked_warning_text().lower()


def test_uc14_04_completion_indicator_boundary_check_zero_completed(authenticated_driver):
    """TC_UC14_04 - Completion Indicator Boundary Check (Zero Completed)."""
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 UC14 Zero")
    dashboard = DashboardPage(driver)

    completion_text = dashboard.get_completion_indicator_text().lower()
    assert "0 of" in completion_text or completion_text.strip().startswith("0")


def test_uc14_05_collaborative_rbac_validation_in_post_planning_tabs(authenticated_driver, second_authenticated_driver):
    """TC_UC14_05 - Collaborative RBAC Validation in Post-Planning Tabs."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 UC14 Viewer Tabs")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    join_trip_via_invite(second_authenticated_driver, invite_link)

    dashboard_viewer = DashboardPage(second_authenticated_driver)
    assert dashboard_viewer.tab_is_reachable("packing_tab", timeout=5), "Viewers can view unlocked tabs"
    dashboard_viewer.open_tab("packing_tab")

    from pages.packing_page import PackingPage
    packing_viewer = PackingPage(second_authenticated_driver)
    assert packing_viewer.modification_controls_are_locked(item_index=0, timeout=3), (
        "Post-scheduling tabs must load for Viewers but stay read-only"
    )
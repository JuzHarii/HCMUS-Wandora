"""Browser-level PA4 tests for UC08 - Shared Luggage Planning."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.support.ui import WebDriverWait

from config import AI_TIMEOUT, SELECTORS
from pages.members_page import MembersPage
from pages.packing_page import PackingPage
from helpers import create_saved_trip, join_trip_via_invite


def test_uc08_01_luggage_responsibility_assignment(authenticated_driver, second_authenticated_driver):
    """TC_UC08_01 - Luggage Responsibility Assignment (Basic Flow)."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Halong")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    join_trip_via_invite(second_authenticated_driver, invite_link)

    packing = PackingPage(owner_driver).open_tab()
    packing.generate_checklist()
    WebDriverWait(owner_driver, AI_TIMEOUT).until(lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"]))

    packing.assign_item(item_index=0, assignee_name="PA4 Second User")

    packing_b = PackingPage(second_authenticated_driver).open_tab()
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["personal_checklist_view"])
    )
    assert packing_b.driver.find_elements("css selector", SELECTORS["personal_checklist_view"])


def test_uc08_02_completion_box_toggle_real_time_sync(authenticated_driver, second_authenticated_driver):
    """TC_UC08_02 - Completion Box Toggle Real-Time Sync."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Vung Tau")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    join_trip_via_invite(second_authenticated_driver, invite_link)

    packing_a = PackingPage(owner_driver).open_tab()
    packing_a.generate_checklist()
    WebDriverWait(owner_driver, AI_TIMEOUT).until(lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"]))

    packing_b = PackingPage(second_authenticated_driver).open_tab()
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"])
    )

    packing_a.toggle_item_complete(item_index=0)

    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: packing_b.is_item_checked(item_index=0)
    )


def test_uc08_03_concurrent_modification_race_condition(authenticated_driver, second_authenticated_driver, third_authenticated_driver):
    """TC_UC08_03 - Concurrent Modification Race Condition (Alternative Flow 1)."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Con Dao")
    invite_link_b = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Editor").get_invite_link()
    join_trip_via_invite(second_authenticated_driver, invite_link_b)
    invite_link_c = MembersPage(owner_driver).invite(third_authenticated_driver.pa4_email, "Editor").get_invite_link()
    join_trip_via_invite(third_authenticated_driver, invite_link_c)

    packing_a = PackingPage(owner_driver).open_tab()
    packing_a.generate_checklist()
    WebDriverWait(owner_driver, AI_TIMEOUT).until(lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"]))
    packing_b = PackingPage(second_authenticated_driver).open_tab()
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"]))

    # User_A assigns to self, User_B assigns the same item to User_C, back
    # to back -- the later write should win once both requests land.
    packing_a.assign_item(item_index=0, assignee_name="PA4 Test User")
    packing_b.assign_item(item_index=0, assignee_name="PA4 Third User")

    owner_driver.refresh()
    WebDriverWait(owner_driver, AI_TIMEOUT).until(lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"]))
    rows = owner_driver.find_elements("css selector", SELECTORS["packing_item_row"])
    assert "Third User" in rows[0].text


def test_uc08_04_add_custom_luggage_item_to_shared_list(authenticated_driver):
    """TC_UC08_04 - Add Custom Luggage Item to Shared List."""
    driver = authenticated_driver
    create_saved_trip(driver, destination_prefix="PA4 Quy Nhon")

    packing = PackingPage(driver).open_tab()
    packing.add_custom_item("Board Games")

    WebDriverWait(driver, AI_TIMEOUT).until(
        lambda d: any("Board Games" in row.text for row in d.find_elements("css selector", SELECTORS["packing_item_row"]))
    )


def test_uc08_05_viewer_modification_permission_check(authenticated_driver, second_authenticated_driver):
    """TC_UC08_05 - Viewer Modification Permission Check."""
    owner_driver = authenticated_driver
    create_saved_trip(owner_driver, destination_prefix="PA4 Ninh Binh")
    invite_link = MembersPage(owner_driver).invite(second_authenticated_driver.pa4_email, "Viewer").get_invite_link()
    join_trip_via_invite(second_authenticated_driver, invite_link)

    packing_a = PackingPage(owner_driver).open_tab()
    packing_a.generate_checklist()
    WebDriverWait(owner_driver, AI_TIMEOUT).until(lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"]))

    packing_viewer = PackingPage(second_authenticated_driver).open_tab()
    WebDriverWait(second_authenticated_driver, AI_TIMEOUT).until(
        lambda d: d.find_elements("css selector", SELECTORS["packing_item_row"])
    )
    assert packing_viewer.modification_controls_are_locked(item_index=0, timeout=3), (
        "Viewer must not be able to modify other members' packing items"
    )
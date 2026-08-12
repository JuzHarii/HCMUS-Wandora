"""
test_uc01_trip_creation.py
----------------------------
Functional (black-box, UI-level) tests for:

    UC01 - Trip Creation and Preference Input

Each test function implements one row of the test-case spreadsheet
(Function 01 sheet, IDs TC_UC01_01 .. TC_UC01_05). The docstring on
each test quotes the matching Test Case ID so results can be traced
straight back to the spreadsheet.

These tests only drive the browser through the real UI: no direct
database access, no importing backend modules. That's what "low
dependency on backend code" means here -- the backend is treated as a
black box, exactly the way a real user experiences it.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # allow `import config`, `import pages`

from pages.login_page import LoginPage
from pages.trip_creation_page import TripCreationPage
from config import AI_TIMEOUT


def test_uc01_01_successful_trip_creation(driver):
    """TC_UC01_01 - Successful Trip Creation (Basic Flow).

    Steps (per Basic Flow 1-4 of UC01):
      1. Log in, click "Create New Trip".
      2/3. Fill destination, dates, capacity, budget, style; click Continue.
    Expected:
      - Trip is created with 'Draft' status.
      - UC02 (AI Itinerary Generator) is triggered automatically.
    """
    LoginPage(driver).login_as("owner")

    trip_page = TripCreationPage(driver)
    trip_page.open_dashboard()
    trip_page.start_new_trip()
    trip_page.fill_trip_form(
        destination="Paris",
        start_date="2026-09-01",
        end_date="2026-09-10",
        capacity="4",
        budget="Medium",
        style="Cultural",
    )
    trip_page.submit()

    assert trip_page.get_trip_status().strip().lower() == "draft", (
        "Expected new trip to be created with 'Draft' status"
    )
    assert trip_page.ai_generation_started(timeout=AI_TIMEOUT), (
        "Expected AI Itinerary Generator (UC02) to auto-trigger via <<include>>"
    )


def test_uc01_02_missing_destination_blocks_submission(driver):
    """TC_UC01_02 - Trip Creation Fails - Missing Destination
    (Alternative Flow 1).

    Steps:
      1. Click "Create New Trip".
      2. Leave Destination empty, fill valid dates.
      3. Click Continue.
    Expected:
      - Submission halts.
      - Validation alert: "Please fill in all required trip details."
    """
    LoginPage(driver).login_as("owner")

    trip_page = TripCreationPage(driver)
    trip_page.open_dashboard()
    trip_page.start_new_trip()
    trip_page.fill_trip_form(start_date="2026-09-01", end_date="2026-09-10")
    trip_page.submit()

    assert trip_page.has_validation_alert(), "Expected a validation alert to appear"
    assert "please fill in all required trip details" in trip_page.get_validation_alert_text().lower()


def test_uc01_03_missing_dates_blocks_submission(driver):
    """TC_UC01_03 - Trip Creation Fails - Missing Dates
    (Alternative Flow 1).

    Steps:
      1. Click "Create New Trip".
      2. Fill Destination only, leave Travel Dates empty.
      3. Click Continue.
    Expected:
      - Submission halts with the same required-field validation alert.
    """
    LoginPage(driver).login_as("owner")

    trip_page = TripCreationPage(driver)
    trip_page.open_dashboard()
    trip_page.start_new_trip()
    trip_page.fill_trip_form(destination="Tokyo")
    trip_page.submit()

    assert trip_page.has_validation_alert(), "Expected a validation alert to appear"
    assert "please fill in all required trip details" in trip_page.get_validation_alert_text().lower()


def test_uc01_04_guest_is_redirected_to_login(driver):
    """TC_UC01_04 - Access Control Interception for Guests
    (Alternative Flow 2).

    Steps:
      1. Log out / clear session.
      2. Attempt to directly open the trip-creation URL.
    Expected:
      - The Auth & RBAC layer redirects the unauthenticated guest to Login.
    """
    login_page = LoginPage(driver)
    login_page.open_login()
    login_page.logout()  # ensure no leftover session/cookies

    trip_page = TripCreationPage(driver)
    trip_page.open("/trips/new")

    assert login_page.is_on_login_page(), (
        f"Expected redirect to Login, but landed on {trip_page.current_url()}"
    )


def test_uc01_05_end_date_before_start_date_is_rejected(driver):
    """TC_UC01_05 - Logical Date Boundary Check.

    Steps:
      1. Click "Create New Trip".
      2. Fill Destination = London, dates so that end date < start date.
      3. Click Continue.
    Expected:
      - Validation fails with a logical date-order error message.
    """
    LoginPage(driver).login_as("owner")

    trip_page = TripCreationPage(driver)
    trip_page.open_dashboard()
    trip_page.start_new_trip()
    trip_page.fill_trip_form(
        destination="London",
        start_date="2026-09-10",
        end_date="2026-09-01",  # end before start -- invalid on purpose
    )
    trip_page.submit()

    assert trip_page.has_validation_alert(), "Expected a date-order validation alert"
    assert "end date must be after or equal to start date" in trip_page.get_validation_alert_text().lower()

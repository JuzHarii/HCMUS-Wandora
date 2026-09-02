"""
conftest.py
------------
Shared pytest fixtures. Handles opening/closing a browser and saving a
screenshot whenever a PA4 test fails.

driver / authenticated_driver are the primary/"current user" session,
used by every single-user test (UC01, UC02, UC04 basic flow, etc).
 
second_driver / second_authenticated_driver are an independent second
browser session + account, used by tests that need two collaborators at
once (UC03 Viewer/Editor checks, UC05 invite acceptance, UC06 role
changes, UC08 luggage sync, UC15 voting/comments).
"""

import os
import datetime
import shutil
import tempfile
from uuid import uuid4
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import BROWSER, HEADLESS, DEFAULT_TIMEOUT, SELECTORS
from pages.auth_page import AuthPage
from pages.trip_creation_page import TripCreationPage

os.environ.setdefault("MOZ_WEBRENDER", "software")

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


def _build_driver():
    if BROWSER == "edge":
        options = EdgeOptions()
        if HEADLESS:
            options.add_argument("--headless=new")
        driver = webdriver.Edge(options=options)
        return driver

    # default: chrome
    options = ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    driver = webdriver.Chrome(options=options)
    return driver


def _sign_up_new_user(driver, label, next_path = None):
    email = f"pa4-e2e-{uuid4().hex[:12]}@example.com"
    AuthPage(driver).open_signup(next_path).sign_up(label, email, "TravelPass123!")
    driver.pa4_email = email
    return driver


@pytest.fixture
def driver():
    """One browser session per test -- the primary/"current user" session."""
    drv = _build_driver()
    drv.implicitly_wait(0)  # we use explicit waits everywhere instead
    yield drv
    drv.quit()


@pytest.fixture
def authenticated_driver(driver):
    """Register a fresh account through the UI and land on the protected UC01 page."""
    _sign_up_new_user(driver, "Owner User", "%2Ftrips%2Fnew")
    TripCreationPage(driver).wait_visible("[data-testid='trip-invitation-continue']")
    return driver


@pytest.fixture
def second_driver():
    """A fully independent browser session used alongside driver for multi-user tests."""
    drv = _build_driver()
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


@pytest.fixture
def second_authenticated_driver(second_driver):
    """Multi-user tests invite this account's email into a trip (as Editor or Viewer, via pages.members_page.MembersPage.invite) and then have it open the returned invite link directly."""
    _sign_up_new_user(second_driver, "Second User")
    WebDriverWait(second_driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["trip_dashboard"]))
    )
    return second_driver


@pytest.fixture
def third_driver():
    """A third independent browser session, for the handful of tests that need three simultaneous collaborators (e.g. UC15 tie-vote resolution)."""
    drv = _build_driver()
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


@pytest.fixture
def third_authenticated_driver(third_driver):
    _sign_up_new_user(third_driver, "Third User")
    WebDriverWait(third_driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", SELECTORS["trip_dashboard"]))
    )
    return third_driver


@pytest.fixture(autouse=True)
def _screenshot_on_failure(request, driver):
    """After each test, if it failed, save a screenshot of every driver
    fixture used by that test."""
    yield
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        for fixture_name in ("driver", "second_driver", "third_driver"):
            if fixture_name in request.node.funcargs:
                driver = request.node.funcargs[fixture_name]
                path = os.path.join(SCREENSHOT_DIR, f"{request.node.name}_{fixture_name}_{timestamp}.png")
                driver.save_screenshot(path)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose the test result on the item so the fixture above can check
    pass/fail (pytest doesn't do this by default)."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

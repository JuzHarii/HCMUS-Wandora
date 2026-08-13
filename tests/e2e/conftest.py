"""
conftest.py
------------
Shared pytest fixtures. Handles opening/closing a browser and saving a
screenshot whenever a PA4 UC01/UC02 test fails.
"""

import os
import datetime
from uuid import uuid4
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from config import BROWSER, HEADLESS
from pages.auth_page import AuthPage
from pages.trip_creation_page import TripCreationPage

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


def _build_driver():
    if BROWSER == "edge":
        options = EdgeOptions()
        if HEADLESS:
            options.add_argument("--headless=new")
        return webdriver.Edge(options=options)

    # default: chrome
    options = ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    return webdriver.Chrome(options=options)


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
    email = f"pa4-e2e-{uuid4().hex[:12]}@example.com"
    AuthPage(driver).open_signup("%2Ftrips%2Fnew").sign_up("PA4 Test User", email, "TravelPass123!")
    TripCreationPage(driver).wait_visible("[data-testid='trip-creation-form']")
    return driver


@pytest.fixture(autouse=True)
def _screenshot_on_failure(request, driver):
    """After each test, if it failed, save a screenshot of every driver
    fixture used by that test."""
    yield
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(SCREENSHOT_DIR, f"{request.node.name}_driver_{timestamp}.png")
        driver.save_screenshot(path)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose the test result on the item so the fixture above can check
    pass/fail (pytest doesn't do this by default)."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

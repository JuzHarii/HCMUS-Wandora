"""
conftest.py
------------
Shared pytest fixtures. Handles opening/closing the browser and taking a
screenshot automatically whenever a test fails (used for the test
report's evidence, e.g. `screenshots/test_uc08_.._2026-08-12.png`).
"""

import os
import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from config import BROWSER, HEADLESS

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
def second_driver():
    """A second, independent browser session for tests that need two
    users interacting at the same time (real-time sync / concurrency
    scenarios in UC08)."""
    drv = _build_driver()
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


@pytest.fixture(autouse=True)
def _screenshot_on_failure(request):
    """After each test, if it failed, save a screenshot of every driver
    fixture used by that test."""
    yield
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        for fixture_name in ("driver", "second_driver"):
            if fixture_name in request.fixturenames:
                drv = request.getfixturevalue(fixture_name)
                path = os.path.join(
                    SCREENSHOT_DIR, f"{request.node.name}_{fixture_name}_{timestamp}.png"
                )
                drv.save_screenshot(path)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose the test result on the item so the fixture above can check
    pass/fail (pytest doesn't do this by default)."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

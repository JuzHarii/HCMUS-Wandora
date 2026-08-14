"""
conftest.py
------------
Shared pytest fixtures. Handles opening/closing a browser and saving a
screenshot whenever a PA4 UC01/UC02 test fails.
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
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from config import BROWSER, HEADLESS
from pages.auth_page import AuthPage
from pages.trip_creation_page import TripCreationPage

os.environ.setdefault("MOZ_WEBRENDER", "software")

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_CHROMEDRIVER = os.path.join(PROJECT_ROOT, "tools", "chromedriver", "chromedriver-win64", "chromedriver.exe")
DEFAULT_CHROME_BINARY = os.path.join(PROJECT_ROOT, "tools", "chrome-for-testing", "chrome-win64", "chrome.exe")
DEFAULT_GECKODRIVER = os.path.join(PROJECT_ROOT, "tools", "geckodriver", "geckodriver.exe")
E2E_EVIDENCE_DIR = os.path.join(PROJECT_ROOT, "pa", "PA4", "evidence", "e2e")


def _build_driver():
    profile_dir = tempfile.mkdtemp(prefix="wandora-e2e-")
    if BROWSER == "edge":
        options = EdgeOptions()
        if HEADLESS:
            options.add_argument("--headless=new")
        driver = webdriver.Edge(options=options)
        driver._wandora_profile_dir = profile_dir
        return driver

    if BROWSER == "firefox":
        options = FirefoxOptions()
        options.page_load_strategy = "eager"
        options.set_preference("network.proxy.type", 0)
        options.set_preference("network.trr.mode", 5)
        options.set_preference("gfx.webrender.force-disabled", True)
        options.set_preference("layers.acceleration.disabled", True)
        if HEADLESS:
            options.add_argument("-headless")
        options.add_argument("-profile")
        options.add_argument(profile_dir)
        driver_path = os.environ.get("WANDORA_GECKODRIVER", DEFAULT_GECKODRIVER)
        if not os.path.exists(driver_path):
            raise FileNotFoundError(
                f"GeckoDriver was not found at {driver_path}. Set WANDORA_GECKODRIVER to a local driver."
            )
        driver = webdriver.Firefox(
            service=FirefoxService(executable_path=driver_path, service_args=["--allow-system-access"]),
            options=options,
        )
        driver._wandora_profile_dir = profile_dir
        return driver

    # default: chrome
    options = ChromeOptions()
    chrome_binary = os.environ.get("WANDORA_CHROME_BINARY", DEFAULT_CHROME_BINARY)
    if os.path.exists(chrome_binary):
        options.binary_location = chrome_binary
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-gpu")
    driver_path = os.environ.get("WANDORA_CHROMEDRIVER", DEFAULT_CHROMEDRIVER)
    if not os.path.exists(driver_path):
        raise FileNotFoundError(
            f"ChromeDriver was not found at {driver_path}. Set WANDORA_CHROMEDRIVER to a matching local driver."
        )
    driver = webdriver.Chrome(service=ChromeService(executable_path=driver_path), options=options)
    driver._wandora_profile_dir = profile_dir
    return driver


@pytest.fixture
def driver():
    """One browser session per test -- the primary/"current user" session."""
    drv = _build_driver()
    drv.implicitly_wait(0)  # we use explicit waits everywhere instead
    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()
    shutil.rmtree(drv._wandora_profile_dir, ignore_errors=True)


@pytest.fixture
def authenticated_driver(driver):
    """Register a fresh account through the UI and land on the protected UC01 page."""
    email = f"pa4-e2e-{uuid4().hex[:12]}@example.com"
    AuthPage(driver).open_signup("%2Ftrips%2Fnew").sign_up("PA4 Test User", email, "TravelPass123!")
    TripCreationPage(driver).wait_visible("[data-testid='trip-invitation-continue']")
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


@pytest.fixture(autouse=True)
def _capture_e2e_evidence_on_success(request, driver):
    """Keep browser screenshots from successful UC01/UC02 E2E cases for PA4 evidence."""
    yield
    if getattr(request.node, "rep_call", None) and request.node.rep_call.passed:
        os.makedirs(E2E_EVIDENCE_DIR, exist_ok=True)
        driver.save_screenshot(os.path.join(E2E_EVIDENCE_DIR, f"{request.node.name}.png"))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose the test result on the item so the fixture above can check
    pass/fail (pytest doesn't do this by default)."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

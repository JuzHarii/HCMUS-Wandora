import datetime
import os
import shutil
import tempfile
from uuid import uuid4

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from config import BROWSER, HEADLESS, SELECTORS
from pages.auth_page import AuthPage
from pages.trip_creation_page import TripCreationPage

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


def _build_driver():
    profile_dir = tempfile.mkdtemp(prefix="wandora-e2e-")

    if BROWSER == "edge":
        options = EdgeOptions()
        if HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1366,900")
        options.add_argument(f"--user-data-dir={profile_dir}")
        driver_path = os.environ.get("WANDORA_EDGEDRIVER")
        service = EdgeService(executable_path=driver_path) if driver_path else None
        driver = webdriver.Edge(service=service, options=options)
    elif BROWSER == "firefox":
        options = FirefoxOptions()
        if HEADLESS:
            options.add_argument("-headless")
        driver_path = os.environ.get("WANDORA_GECKODRIVER")
        service = FirefoxService(executable_path=driver_path) if driver_path else None
        driver = webdriver.Firefox(service=service, options=options)
    else:
        options = ChromeOptions()
        chrome_binary = os.environ.get("WANDORA_CHROME_BINARY")
        if chrome_binary:
            options.binary_location = chrome_binary
        if HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1366,900")
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        driver_path = os.environ.get("WANDORA_CHROMEDRIVER")
        service = ChromeService(executable_path=driver_path) if driver_path else None
        driver = webdriver.Chrome(service=service, options=options)

    driver._wandora_profile_dir = profile_dir
    return driver


@pytest.fixture
def driver():
    drv = _build_driver()
    drv.implicitly_wait(0)
    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()
    shutil.rmtree(drv._wandora_profile_dir, ignore_errors=True)


@pytest.fixture
def authenticated_driver(driver):
    email = f"pa5-e2e-{uuid4().hex[:12]}@example.com"
    AuthPage(driver).open_signup("%2Ftrips%2Fnew").sign_up("PA5 Test User", email, "TravelPass123!")
    TripCreationPage(driver).wait_visible(SELECTORS["trip_invitation_continue"])
    return driver


@pytest.fixture(autouse=True)
def _screenshot_on_failure(request, driver):
    yield
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(SCREENSHOT_DIR, f"{request.node.name}_{timestamp}.png")
        driver.save_screenshot(path)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

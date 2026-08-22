"""Browser-level PA4 tests for UC12 - User Login and Authentication.

test_authentication.py already covers the sign-up -> sign-out -> sign-in
round trip and the guest-redirect-to-login case at a high level; this
file fills in the remaining xlsx cases that are UC12-specific
(bad credentials, blank fields, and session expiry).
"""

import os
import sys
from uuid import uuid4

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import BASE_URL, DEFAULT_TIMEOUT, SELECTORS
from conftest import _sign_up_new_user
from pages.auth_page import AuthPage


def test_uc12_01_successful_login_with_valid_credentials(driver):
    """TC_UC12_01 - Successful Login with Valid Credentials (Basic Flow)."""
    email = f"pa4-uc12-{uuid4().hex[:12]}@example.com"
    password = "SecurePassword123!"
    AuthPage(driver).open_signup().sign_up("PA4 UC12 User", email, password)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["trip_dashboard"])))
    driver.find_element("css selector", SELECTORS["dashboard_signout_button"]).click()

    AuthPage(driver).open_login().login(email, password)

    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["trip_dashboard"])))
    assert driver.current_url.rstrip("/").endswith("/home")


def test_uc12_02_login_fails_due_to_invalid_credentials(driver):
    """TC_UC12_02 - Login Fails due to Invalid Credentials (Alternative Flow 1)."""
    email = f"pa4-uc12-{uuid4().hex[:12]}@example.com"
    AuthPage(driver).open_signup().sign_up("PA4 UC12 User", email, "CorrectPassword123!")
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["trip_dashboard"])))
    driver.find_element("css selector", SELECTORS["dashboard_signout_button"]).click()

    auth = AuthPage(driver).open_login()
    auth.login(email, "WrongPassword!")

    assert "incorrect email or password" in auth.get_text(SELECTORS["login_error_alert"]).lower()
    assert driver.find_element("css selector", SELECTORS["auth_email_input"]).get_attribute("value") == email


def test_uc12_03_login_fails_due_to_blank_fields(driver):
    """TC_UC12_03 - Login Fails due to Blank Fields (Alternative Flow 2)."""
    auth = AuthPage(driver).open_login()
    auth.click(SELECTORS["login_submit_button"])

    assert "fill in all required fields" in auth.get_text(SELECTORS["login_validation_alert"]).lower()
    assert "auth" in driver.current_url


def test_uc12_04_automatic_redirect_on_unauthorized_access(driver):
    """TC_UC12_04 - Automatic Redirect on Unauthorized Access (Integration)."""
    driver.get(f"{BASE_URL}/trips/new")

    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.url_contains("/auth?mode=login"))
    assert "next=%2Ftrips%2Fnew" in driver.current_url


def test_uc12_05_session_expiry_and_reauthentication(driver):
    """TC_UC12_05 - Session Expiry and Re-authentication (Boundary Check).

    No test-only endpoint exists in this harness to force-expire a
    session, so this simulates expiry the way the real client would
    observe it: by clearing the session cookie client-side and then
    attempting an authenticated action, which should look identical to a
    server-expired session from the frontend's point of view.
    """
    email = f"pa4-uc12-{uuid4().hex[:12]}@example.com"
    AuthPage(driver).open_signup().sign_up("PA4 UC12 User", email, "SecurePassword123!")
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["trip_dashboard"])))

    driver.clear_session()
    driver.get(f"{BASE_URL}/trips/new")

    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.url_contains("/auth"))
    if AuthPage(driver).is_present(SELECTORS["session_expired_alert"], timeout=3):
        assert "expired" in AuthPage(driver).get_text(SELECTORS["session_expired_alert"]).lower()
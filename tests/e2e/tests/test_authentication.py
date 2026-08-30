"""Browser checks for registration, protected routes, and returning sign-in."""

import os
import sys
from uuid import uuid4

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import BASE_URL, DEFAULT_TIMEOUT, SELECTORS
from pages.auth_page import AuthPage


def test_root_is_the_public_landing_page(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.visibility_of_element_located(("css selector", "#hero-title")))
    assert driver.current_url.rstrip("/") == BASE_URL.rstrip("/")


def test_user_can_sign_up_sign_out_and_sign_in_again(driver):
    email = f"pa4-auth-{uuid4().hex[:12]}@example.com"
    password = "TravelPass123!"

    AuthPage(driver).open_signup().sign_up("PA4 Auth User", email, password)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["trip_dashboard"])))

    assert driver.current_url.rstrip("/").endswith("/home")

    driver.get(BASE_URL)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.visibility_of_element_located(("css selector", "#hero-title")))

    driver.get(f"{BASE_URL}/home")
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.element_to_be_clickable(("css selector", SELECTORS["dashboard_signout_button"]))
    ).click()

    AuthPage(driver).open_login().login(email, password)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.visibility_of_element_located(("css selector", SELECTORS["trip_dashboard"])))
    assert driver.current_url.rstrip("/").endswith("/home")

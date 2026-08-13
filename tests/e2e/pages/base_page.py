"""
base_page.py
------------
Small wrapper around Selenium so test files never call `driver.find_element`
directly. Every method here does ONE readable thing (click a thing, read a
thing, wait for a thing) and always waits for the element first, which
avoids flaky "element not found" failures caused by React/JS rendering
delays.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import DEFAULT_TIMEOUT, BASE_URL


class BasePage:
    def __init__(self, driver, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        self.timeout = timeout

    # -- navigation ----------------------------------------------------
    def open(self, path=""):
        """Navigate to BASE_URL + path, e.g. open('/trips/new')."""
        self.driver.get(BASE_URL.rstrip("/") + path)
        return self

    # -- waits / lookups -------------------------------------------------
    def wait_visible(self, css_selector, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def wait_clickable(self, css_selector, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )

    def wait_gone(self, css_selector, timeout=None):
        """Wait until an element disappears (e.g. a loading spinner)."""
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def is_present(self, css_selector, timeout=3):
        """Non-failing check: True/False instead of raising TimeoutException."""
        try:
            self.wait_visible(css_selector, timeout=timeout)
            return True
        except Exception:
            return False

    # -- actions ---------------------------------------------------------
    def click(self, css_selector):
        self.wait_clickable(css_selector).click()
        return self

    def type_text(self, css_selector, text, clear_first=True):
        field = self.wait_visible(css_selector)
        if clear_first:
            field.clear()
        field.send_keys(text)
        return self

    def get_text(self, css_selector):
        return self.wait_visible(css_selector).text

    def current_url(self):
        return self.driver.current_url

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import BASE_URL, DEFAULT_TIMEOUT


class BasePage:
    def __init__(self, driver, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        self.timeout = timeout

    def open(self, path=""):
        self.driver.get(f"{BASE_URL}{path}")
        return self

    def wait_visible(self, css_selector, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def wait_clickable(self, css_selector, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )

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

    def elements(self, css_selector):
        return self.driver.find_elements(By.CSS_SELECTOR, css_selector)

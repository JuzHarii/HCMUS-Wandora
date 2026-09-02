from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import BASE_URL, DEFAULT_TIMEOUT


def test_protected_trip_route_redirects_guest_to_login(driver):
    driver.get(f"{BASE_URL}/trips/new")

    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.url_contains("/auth?mode=login"))
    assert "next=%2Ftrips%2Fnew" in driver.current_url


def test_root_is_public_landing_page(driver):
    driver.get(BASE_URL)

    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(("css selector", "#hero-title"))
    )
    assert driver.current_url.rstrip("/") == BASE_URL

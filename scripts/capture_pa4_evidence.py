"""Capture three browser evidence screenshots for the PA4 UC01/UC02 report."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIRECTORY = REPOSITORY_ROOT / "pa" / "PA4" / "evidence"
BASE_URL = os.environ.get("WANDORA_BASE_URL", "http://127.0.0.1:5173").rstrip("/")


def set_react_date(driver: webdriver.Chrome, selector: str, value: str) -> None:
    field = driver.find_element(By.CSS_SELECTOR, selector)
    driver.execute_script(
        "const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; setter.call(arguments[0], arguments[1]); arguments[0].dispatchEvent(new Event('input', {bubbles: true})); arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
        field,
        value,
    )


def main() -> None:
    EVIDENCE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)
    try:
        driver.get(BASE_URL)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".hero-section")))
        driver.save_screenshot(str(EVIDENCE_DIRECTORY / "01-landing-page.png"))

        driver.get(f"{BASE_URL}/trips/new")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='trip-creation-form']")))
        driver.save_screenshot(str(EVIDENCE_DIRECTORY / "02-uc01-trip-creation.png"))

        driver.find_element(By.CSS_SELECTOR, "[data-testid='trip-destination']").send_keys(f"PA4 evidence {uuid4().hex[:6]}")
        set_react_date(driver, "[data-testid='trip-start-date']", "2026-09-01")
        set_react_date(driver, "[data-testid='trip-end-date']", "2026-09-03")
        Select(driver.find_element(By.CSS_SELECTOR, "[data-testid='trip-style']")).select_by_visible_text("Cultural")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='trip-continue-button']").click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='itinerary-view']")))
        driver.save_screenshot(str(EVIDENCE_DIRECTORY / "03-uc02-generated-itinerary.png"))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

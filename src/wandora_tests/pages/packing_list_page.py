"""
packing_list_page.py
----------------------
Page object for UC08: Shared Luggage Planning.

Mirrors the Basic Flow from the Use-Case Specification:
  1. Open the Packing List.
  2. Check/uncheck items or assign an item to a member.
  3. Add custom items.
  4. Item status/assignment syncs in real time across sessions.

Row lookups use the item's visible name (e.g. "Tent") rather than an
index, since that's how a human tester finds the row too.
"""

from selenium.webdriver.common.by import By

from config import SELECTORS, BASE_URL, SHARED_TRIP_ID
from pages.base_page import BasePage


class PackingListPage(BasePage):
    def open_packing_list(self, trip_id=SHARED_TRIP_ID):
        self.open(f"/trips/{trip_id}/packing-list")
        return self

    def _row(self, item_name):
        """Return the row element for a given item name, waited for."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, SELECTORS["packing_item_row"])
        for row in rows:
            if item_name.strip().lower() in row.text.strip().lower():
                return row
        raise AssertionError(f"Packing item '{item_name}' not found in list")

    def assign_item(self, item_name, assignee_name):
        row = self._row(item_name)
        select_el = row.find_element(By.CSS_SELECTOR, SELECTORS["packing_item_assignee_select"])
        # Simple <select>-based assignment; if the real UI uses a custom
        # dropdown component, swap this for the matching click sequence.
        select_el.click()
        option = row.find_element(By.XPATH, f".//option[normalize-space(text())='{assignee_name}']")
        option.click()
        return self

    def get_assignee(self, item_name):
        row = self._row(item_name)
        avatar = row.find_element(By.CSS_SELECTOR, SELECTORS["packing_item_assignee_avatar"])
        return avatar.get_attribute("data-assignee-name") or avatar.text

    def check_item(self, item_name):
        row = self._row(item_name)
        checkbox = row.find_element(By.CSS_SELECTOR, SELECTORS["packing_item_checkbox"])
        if not checkbox.is_selected():
            checkbox.click()
        return self

    def is_item_checked(self, item_name):
        row = self._row(item_name)
        checkbox = row.find_element(By.CSS_SELECTOR, SELECTORS["packing_item_checkbox"])
        return checkbox.is_selected()

    def is_item_checkbox_enabled(self, item_name):
        row = self._row(item_name)
        checkbox = row.find_element(By.CSS_SELECTOR, SELECTORS["packing_item_checkbox"])
        return checkbox.is_enabled()

    def add_custom_item(self, item_name):
        self.click(SELECTORS["add_custom_item_button"])
        self.type_text(SELECTORS["custom_item_name_input"], item_name)
        self.click(SELECTORS["custom_item_save_button"])
        return self

    def item_exists(self, item_name, timeout=5):
        try:
            self.wait_visible(SELECTORS["packing_item_row"], timeout=timeout)
            self._row(item_name)
            return True
        except Exception:
            return False

    def permission_denied_shown(self, timeout=5):
        return self.is_present(SELECTORS["permission_denied_toast"], timeout=timeout)

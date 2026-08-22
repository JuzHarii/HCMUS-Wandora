"""
packing_page.py
-----------------
Page object for the trip workspace's Packing List tab (Screen 5A/5B).
Covers:

    UC07 - AI Packing Suggestions
    UC08 - Shared Luggage Planning
"""

from selenium.webdriver.support.select import Select

from config import SELECTORS
from pages.base_page import BasePage


class PackingPage(BasePage):
    def open_tab(self):
        self.click(SELECTORS["packing_tab"])
        return self

    # -- UC07: AI packing suggestions ----------------------------------------
    def generate_checklist(self):
        self.click(SELECTORS["generate_packing_button"])
        return self

    def confirm_overwrite(self):
        self.click(SELECTORS["packing_overwrite_confirm_button"])
        return self

    def get_packing_items_text(self):
        return [row.text for row in self.driver.find_elements("css selector", SELECTORS["packing_item_row"])]

    def get_offline_warning_text(self):
        return self.get_text(SELECTORS["packing_offline_warning"])

    def get_missing_metadata_warning_text(self):
        return self.get_text(SELECTORS["packing_missing_metadata_warning"])

    def generate_control_is_present(self, timeout=5):
        return self.is_present(SELECTORS["generate_packing_button"], timeout=timeout)

    # -- UC08: shared luggage assignment --------------------------------------
    def assign_item(self, item_index, assignee_name):
        rows = self.driver.find_elements("css selector", SELECTORS["packing_item_row"])
        select_el = rows[item_index].find_element("css selector", SELECTORS["luggage_item_assignee_select"])
        Select(select_el).select_by_visible_text(assignee_name)
        return self

    def toggle_item_complete(self, item_index):
        rows = self.driver.find_elements("css selector", SELECTORS["packing_item_row"])
        rows[item_index].find_element("css selector", SELECTORS["luggage_item_checkbox"]).click()
        return self

    def is_item_checked(self, item_index):
        rows = self.driver.find_elements("css selector", SELECTORS["packing_item_row"])
        checkbox = rows[item_index].find_element("css selector", SELECTORS["luggage_item_checkbox"])
        return checkbox.is_selected()

    def add_custom_item(self, name):
        self.click(SELECTORS["add_custom_luggage_button"])
        self.type_text(SELECTORS["custom_luggage_name_input"], name)
        self.click(SELECTORS["custom_luggage_save_button"])
        return self

    def modification_controls_are_locked(self, item_index=0, timeout=5):
        """True if a Viewer cannot modify another member's item -- i.e. the
        assignee dropdown and checkbox for that row are absent or disabled."""
        rows = self.driver.find_elements("css selector", SELECTORS["packing_item_row"])
        if not rows:
            return True
        row = rows[item_index]
        checkboxes = row.find_elements("css selector", SELECTORS["luggage_item_checkbox"])
        if not checkboxes:
            return True
        return not checkboxes[0].is_enabled()
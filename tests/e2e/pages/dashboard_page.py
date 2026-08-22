"""
dashboard_page.py
-------------------
Page object for the "My Trips" dashboard (Screen 1A/1B) and the trip
workspace chrome around it. Covers:

    UC14 - Post-Scheduling Feature Access (tab unlock / completion indicator)
    UC16 - Duplicate/Similar Trip Detection (shown during UC01 submission)
    UC17 - Trip History (list, open, version history / restore)
"""

from config import SELECTORS
from pages.base_page import BasePage


class DashboardPage(BasePage):
    def open_history(self):
        self.click(SELECTORS["trip_history_link"])
        return self

    def get_trip_cards_text(self):
        return [card.text for card in self.driver.find_elements("css selector", SELECTORS["dashboard_trip_card"])]

    def open_trip_card(self, index=0):
        cards = self.driver.find_elements("css selector", SELECTORS["dashboard_trip_card"])
        cards[index].click()
        return self

    def get_empty_history_text(self):
        return self.get_text(SELECTORS["trip_history_empty_state"])

    # -- UC14: tab access -----------------------------------------------------
    def open_tab(self, testid_key):
        self.click(SELECTORS[testid_key])
        return self

    def tab_is_reachable(self, testid_key, timeout=5):
        return self.is_present(SELECTORS[testid_key], timeout=timeout)

    def get_feature_locked_warning_text(self):
        return self.get_text(SELECTORS["feature_locked_warning"])

    def get_completion_indicator_text(self):
        return self.get_text(SELECTORS["completion_indicator"])

    # -- UC16: duplicate/similar trip detection --------------------------------
    def similar_trip_modal_is_present(self, timeout=5):
        return self.is_present(SELECTORS["similar_trip_modal"], timeout=timeout)

    def use_similar_trip_as_template(self):
        self.click(SELECTORS["similar_trip_use_template_button"])
        return self

    def open_existing_similar_trip(self):
        self.click(SELECTORS["similar_trip_open_existing_button"])
        return self

    def continue_as_new_trip(self):
        self.click(SELECTORS["similar_trip_continue_new_button"])
        return self

    # -- UC17: version history --------------------------------------------------
    def open_version_history(self):
        self.click(SELECTORS["version_history_button"])
        return self

    def restore_version(self, version_index=0):
        items = self.driver.find_elements("css selector", SELECTORS["version_history_item"])
        items[version_index].find_element("css selector", SELECTORS["version_restore_button"]).click()
        return self

    def get_version_history_empty_text(self):
        return self.get_text(SELECTORS["version_history_empty_message"])

    def restore_button_is_present(self, timeout=5):
        return self.is_present(SELECTORS["version_restore_button"], timeout=timeout)
"""
trip_creation_page.py
----------------------
Page object for UC01: Trip Creation and Preference Input.

Mirrors the Basic Flow from the Use-Case Specification:
  1. Click "Create New Trip".
  2. Fill destination / dates / capacity / budget / style.
  3. Click "Continue".
  4. Trip is created as 'Draft' and UC02 (AI generation) auto-triggers.
"""

from config import SELECTORS
from pages.base_page import BasePage


class TripCreationPage(BasePage):
    def open_dashboard(self):
        self.open("/dashboard")
        return self

    def start_new_trip(self):
        self.click(SELECTORS["create_trip_button"])
        self.wait_visible(SELECTORS["trip_form"])
        return self

    def fill_trip_form(
        self,
        destination=None,
        start_date=None,
        end_date=None,
        capacity=None,
        budget=None,
        style=None,
    ):
        """Any field left as None is simply not touched -- this lets each
        test case fill only the fields relevant to that scenario
        (e.g. leaving destination empty for TC_UC01_02)."""
        if destination is not None:
            self.type_text(SELECTORS["trip_destination_input"], destination)
        if start_date is not None:
            self.type_text(SELECTORS["trip_start_date_input"], start_date)
        if end_date is not None:
            self.type_text(SELECTORS["trip_end_date_input"], end_date)
        if capacity is not None:
            self.type_text(SELECTORS["trip_capacity_select"], capacity)
        if budget is not None:
            self.type_text(SELECTORS["trip_budget_select"], budget)
        if style is not None:
            self.type_text(SELECTORS["trip_style_select"], style)
        return self

    def submit(self):
        self.click(SELECTORS["trip_continue_button"])
        return self

    def get_validation_alert_text(self):
        return self.get_text(SELECTORS["trip_validation_alert"])

    def has_validation_alert(self, timeout=5):
        return self.is_present(SELECTORS["trip_validation_alert"], timeout=timeout)

    def get_trip_status(self):
        return self.get_text(SELECTORS["trip_status_badge"])

    def ai_generation_started(self, timeout=None):
        """Post-condition check for the Basic Flow: creating a trip must
        auto-trigger UC02 (AI Itinerary Generator) via <<include>>."""
        return self.is_present(
            SELECTORS["ai_generation_indicator"], timeout=timeout or self.timeout
        )

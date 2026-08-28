"""
trip_creation_page.py
----------------------
Page object for UC01: Trip Creation and Preference Input.

    Mirrors the Basic Flow from the Use-Case Specification. The route is
    protected, so tests must authenticate before opening this page.
"""

from config import SELECTORS
from pages.base_page import BasePage


class TripCreationPage(BasePage):
    def open_trip_creation(self):
        self.open("/trips/new")
        self.click(SELECTORS["trip_invitation_continue"])
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
            self.set_date(SELECTORS["trip_start_date_input"], start_date)
        if end_date is not None:
            self.set_date(SELECTORS["trip_end_date_input"], end_date)
        if capacity is not None:
            self.type_text(SELECTORS["trip_capacity_select"], capacity)
        if budget is not None:
            self.type_text(SELECTORS["trip_budget_select"], budget)
        return self

    def submit(self):
        self.click(SELECTORS["trip_continue_button"])
        return self

    def generate_preview(self):
        self.click(SELECTORS["generate_preview_button"])
        return self

    def save_trip(self):
        self.click(SELECTORS["save_trip_button"])
        return self

    def open_saved_trip(self):
        self.click(SELECTORS["open_trip_workspace"])
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

    def set_date(self, css_selector, value):
        field = self.wait_visible(css_selector)
        self.driver.execute_script(
            "const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; setter.call(arguments[0], arguments[1]); arguments[0].dispatchEvent(new Event('input', {bubbles: true})); arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
            field,
            value,
        )
        return self

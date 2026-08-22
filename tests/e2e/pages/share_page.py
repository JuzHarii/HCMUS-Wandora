"""
share_page.py
---------------
Page object for UC11 - Share or Export Trip Plan.
"""

from selenium.webdriver.support.select import Select

from config import SELECTORS
from pages.base_page import BasePage


class SharePage(BasePage):
    def open_modal(self):
        self.click(SELECTORS["share_export_button"])
        return self

    def generate_view_only_link(self):
        self.click(SELECTORS["generate_share_link_button"])
        access_field = self.wait_visible(SELECTORS["share_access_select"])
        Select(access_field).select_by_visible_text("View-only")
        return self.get_text(SELECTORS["share_link_display"])

    def export_pdf(self):
        self.click(SELECTORS["export_pdf_button"])
        return self

    def revoke_link(self):
        self.click(SELECTORS["revoke_link_button"])
        return self

    def get_revoked_link_warning_text(self):
        return self.get_text(SELECTORS["revoked_link_warning"])

    def get_export_error_text(self):
        return self.get_text(SELECTORS["export_error_alert"])

    def get_export_empty_warning_text(self):
        return self.get_text(SELECTORS["export_empty_itinerary_warning"])

    def export_pdf_button_is_present(self, timeout=5):
        return self.is_present(SELECTORS["export_pdf_button"], timeout=timeout)
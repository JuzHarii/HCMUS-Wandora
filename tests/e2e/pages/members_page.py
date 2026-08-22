"""
members_page.py
-----------------
Page object for the "Members & Settings" modal on a trip workspace.
Covers:

    UC05 - Group Collaboration (invite dispatch, invite acceptance,
           administrative lock, duplicate-invite prevention, expired
           token handling)
    UC06 - Role and Permission Management (role updates, ownership
           transfer, last-owner protection)
"""

from selenium.webdriver.support.select import Select

from config import SELECTORS
from pages.base_page import BasePage


class MembersPage(BasePage):
    def open(self, path=""):
        # Members & Settings is a modal on the trip workspace, not a route
        # of its own -- opening the workspace URL then clicking the button
        # is the real entry point. Kept for BasePage compatibility only.
        return super().open(path)

    def open_modal(self):
        self.click(SELECTORS["members_settings_button"])
        return self

    # -- UC05: invite dispatch ----------------------------------------------
    def invite(self, email, role):
        self.open_modal()
        self.type_text(SELECTORS["member_invite_email_input"], email)
        role_field = self.wait_visible(SELECTORS["member_invite_role_select"])
        Select(role_field).select_by_visible_text(role)
        self.click(SELECTORS["member_invite_send_button"])
        return self

    def get_invite_link(self):
        return self.get_text(SELECTORS["member_invite_link_display"])

    def get_member_rows_text(self):
        return [row.text for row in self.driver.find_elements("css selector", SELECTORS["member_list_item"])]

    def invite_controls_are_visible(self, timeout=5):
        return self.is_present(SELECTORS["members_settings_button"], timeout=timeout)

    def get_invite_permission_denied_text(self):
        return self.get_text(SELECTORS["invite_permission_denied"])

    def get_duplicate_invite_warning_text(self):
        return self.get_text(SELECTORS["invite_duplicate_warning"])

    def get_invalid_token_warning_text(self):
        return self.get_text(SELECTORS["invite_invalid_token_warning"])

    # -- UC06: role management -----------------------------------------------
    def set_member_role(self, member_index, new_role):
        rows = self.driver.find_elements("css selector", SELECTORS["member_list_item"])
        row = rows[member_index]
        select_el = row.find_element("css selector", SELECTORS["member_role_select"])
        Select(select_el).select_by_visible_text(new_role)
        row.find_element("css selector", SELECTORS["member_role_save_button"]).click()
        return self

    def confirm_ownership_transfer(self):
        self.click(SELECTORS["ownership_transfer_confirm_button"])
        return self

    def get_rbac_denied_text(self):
        return self.get_text(SELECTORS["rbac_action_denied_alert"])

    def get_demote_last_owner_error_text(self):
        return self.get_text(SELECTORS["demote_last_owner_error"])

    def self_role_select_is_disabled(self, member_index=0):
        rows = self.driver.find_elements("css selector", SELECTORS["member_list_item"])
        select_el = rows[member_index].find_element("css selector", SELECTORS["member_role_select"])
        return not select_el.is_enabled()
"""
itinerary_page.py
------------------
Page object for the saved-trip Itinerary Workspace (Screen 6A/6B in
UI-Design.docx). Covers everything that happens on the day-by-day timeline
once a trip has been saved:

    UC03 - AI Itinerary Adjustment (prompt-based schedule edits)
    UC04 - Manual Places and External Links (Add Activity / Place)
    UC09 - Manual Place Note Input (editing notes on an existing activity)
    UC15 - Group Member Interaction (comments, alternative proposals, votes)

Also exposes invite_member()/get_invite_link(), a thin convenience wrapper
around the Members & Settings modal that UC03/UC04 tests use to put a
second account into an Editor or Viewer role on the trip before exercising
role-based behaviour. UC05/UC06 tests use the fuller pages.members_page
.MembersPage instead, which points at the same modal.
"""

from selenium.webdriver.support.select import Select

from config import SELECTORS
from pages.base_page import BasePage


class ItineraryPage(BasePage):
    # -- AI adjustment (UC03) ---------------------------------------------
    def request_adjustment(self, prompt_text):
        self.type_text(SELECTORS["itinerary_adjustment_input"], prompt_text)
        self.click(SELECTORS["itinerary_adjustment_submit"])
        return self

    def accept_adjustment(self):
        self.wait_visible(SELECTORS["itinerary_adjustment_preview"])
        self.click(SELECTORS["itinerary_adjustment_accept"])
        return self

    def discard_adjustment(self):
        self.wait_visible(SELECTORS["itinerary_adjustment_preview"])
        self.click(SELECTORS["itinerary_adjustment_discard"])
        return self

    def get_permission_denied_text(self):
        return self.get_text(SELECTORS["permission_denied_modal"])

    def get_conflict_warning_text(self):
        return self.get_text(SELECTORS["adjustment_conflict_warning"])

    def get_adjustment_error_text(self):
        return self.get_text(SELECTORS["adjustment_error_alert"])

    def adjustment_input_is_locked(self, timeout=5):
        """True if the prompt box is hidden/disabled, as it should be for Viewers."""
        if not self.is_present(SELECTORS["itinerary_adjustment_input"], timeout=timeout):
            return True
        field = self.wait_visible(SELECTORS["itinerary_adjustment_input"], timeout=timeout)
        return not field.is_enabled()

    # -- Manual places (UC04) ----------------------------------------------
    def open_add_activity_form(self):
        self.click(SELECTORS["add_activity_button"])
        self.wait_visible(SELECTORS["activity_name_input"])
        return self

    def fill_activity_form(self, name=None, category=None, notes=None, url=None):
        if name is not None:
            self.type_text(SELECTORS["activity_name_input"], name)
        if category is not None:
            select_el = self.wait_visible(SELECTORS["activity_category_select"])
            Select(select_el).select_by_visible_text(category)
        if notes is not None:
            self.type_text(SELECTORS["activity_notes_textarea"], notes)
        if url is not None:
            self.type_text(SELECTORS["activity_url_input"], url)
        return self

    def save_activity(self):
        self.click(SELECTORS["activity_save_button"])
        return self

    def get_activity_validation_text(self):
        return self.get_text(SELECTORS["activity_form_validation_alert"])

    def add_activity_control_is_visible(self, timeout=5):
        return self.is_present(SELECTORS["add_activity_button"], timeout=timeout)

    # -- Notes on an existing activity (UC09) -------------------------------
    def edit_notes(self, activity_index=0):
        rows = self.driver.find_elements("css selector", SELECTORS["activity_row"])
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", rows[activity_index])
        rows[activity_index].find_element("css selector", SELECTORS["edit_notes_button"]).click()
        self.wait_visible(SELECTORS["notes_editor_textarea"])
        return self

    def set_note_text(self, text, clear_first=True):
        self.type_text(SELECTORS["notes_editor_textarea"], text, clear_first=clear_first)
        return self

    def save_notes(self):
        self.click(SELECTORS["notes_save_button"])
        return self

    def edit_notes_control_is_visible(self, activity_index=0, timeout=5):
        rows = self.driver.find_elements("css selector", SELECTORS["activity_row"])
        if not rows:
            return False
        return bool(rows[activity_index].find_elements("css selector", SELECTORS["edit_notes_button"]))

    def get_notes_locked_text(self):
        return self.get_text(SELECTORS["notes_locked_warning"])

    # -- Comments, proposals & voting (UC15) ---------------------------------
    def add_comment(self, activity_index, comment_text):
        rows = self.driver.find_elements("css selector", SELECTORS["activity_row"])
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", rows[activity_index])
        rows[activity_index].find_element("css selector", SELECTORS["activity_comment_input"]).send_keys(comment_text)
        rows[activity_index].find_element("css selector", SELECTORS["activity_comment_submit"]).click()
        return self

    def propose_alternative(self, activity_index, proposal_text):
        rows = self.driver.find_elements("css selector", SELECTORS["activity_row"])
        rows[activity_index].find_element("css selector", SELECTORS["activity_alt_proposal_input"]).send_keys(proposal_text)
        rows[activity_index].find_element("css selector", SELECTORS["activity_alt_proposal_submit"]).click()
        return self

    def vote_on_proposal(self, proposal_index=0):
        proposals = self.driver.find_elements("css selector", SELECTORS["proposal_card"])
        proposals[proposal_index].find_element("css selector", SELECTORS["proposal_vote_button"]).click()
        return self

    def get_vote_count(self, proposal_index=0):
        proposals = self.driver.find_elements("css selector", SELECTORS["proposal_card"])
        return proposals[proposal_index].find_element("css selector", SELECTORS["proposal_vote_count"]).text

    def apply_change_control_is_visible(self, proposal_index=0, timeout=5):
        proposals = self.driver.find_elements("css selector", SELECTORS["proposal_card"])
        if not proposals:
            return False
        return bool(proposals[proposal_index].find_elements("css selector", SELECTORS["apply_change_button"]))

    def get_consensus_status_text(self):
        return self.get_text(SELECTORS["consensus_status"])

    def apply_owner_decision(self, proposal_index=0):
        proposals = self.driver.find_elements("css selector", SELECTORS["proposal_card"])
        proposals[proposal_index].click()
        self.click(SELECTORS["apply_decision_button"])
        return self

    # -- Members & Settings (shared setup helper for UC03/UC04) -------------
    def invite_member(self, email, role):
        """Opens the Members & Settings modal and invites `email` with the
        given `role` ('Editor' or 'Viewer'). Returns the shareable invite
        link so a second browser session can join directly."""
        self.click(SELECTORS["members_settings_button"])
        self.type_text(SELECTORS["member_invite_email_input"], email)
        role_field = self.wait_visible(SELECTORS["member_invite_role_select"])
        Select(role_field).select_by_visible_text(role)
        self.click(SELECTORS["member_invite_send_button"])
        return self.get_text(SELECTORS["member_invite_link_display"])
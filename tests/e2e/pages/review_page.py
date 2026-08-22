"""
review_page.py
----------------
Page object for UC10 - Place Ratings and Reviews. Stars are rendered as a
group of clickable buttons, one per rating value:
    [data-testid='review-star-1'] .. [data-testid='review-star-5']
"""

from config import SELECTORS
from pages.base_page import BasePage


class ReviewPage(BasePage):
    def open_review_form(self, place_index=0):
        buttons = self.driver.find_elements("css selector", SELECTORS["add_review_button"])
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buttons[place_index])
        buttons[place_index].click()
        self.wait_visible(SELECTORS["review_submit_button"])
        return self

    def select_stars(self, stars):
        self.click(f"[data-testid='review-star-{stars}']")
        return self

    def set_review_text(self, text, clear_first=True):
        self.type_text(SELECTORS["review_text_input"], text, clear_first=clear_first)
        return self

    def submit(self):
        self.click(SELECTORS["review_submit_button"])
        return self

    def get_validation_text(self):
        return self.get_text(SELECTORS["review_validation_alert"])

    def get_review_texts(self):
        return [row.text for row in self.driver.find_elements("css selector", SELECTORS["review_display"])]

    def add_review_button_is_present(self, timeout=5):
        return self.is_present(SELECTORS["add_review_button"], timeout=timeout)
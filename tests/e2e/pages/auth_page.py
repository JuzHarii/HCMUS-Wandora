from config import SELECTORS
from pages.base_page import BasePage


class AuthPage(BasePage):
    def open_signup(self, next_path=None):
        path = "/auth?mode=signup"
        if next_path:
            path += f"&next={next_path}"
        self.open(path)
        self.wait_visible(SELECTORS["signup_name_input"])
        return self

    def sign_up(self, full_name, email, password):
        self.type_text(SELECTORS["signup_name_input"], full_name)
        self.type_text(SELECTORS["auth_email_input"], email)
        self.type_text(SELECTORS["auth_password_input"], password)
        self.type_text(SELECTORS["signup_confirm_password_input"], password)
        self.click(SELECTORS["signup_submit_button"])
        return self

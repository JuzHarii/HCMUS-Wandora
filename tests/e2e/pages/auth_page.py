"""Page object for the public sign-up and sign-in screen."""

from config import SELECTORS
from pages.base_page import BasePage


class AuthPage(BasePage):
    def open_signup(self, next_path: str | None = None):
        path = "/auth?mode=signup"
        if next_path:
            path += f"&next={next_path}"
        self.open(path)
        self.wait_visible(SELECTORS["signup_name_input"])
        return self

    def sign_up(self, full_name: str, email: str, password: str):
        self.type_text(SELECTORS["signup_name_input"], full_name)
        self.type_text(SELECTORS["auth_email_input"], email)
        self.type_text(SELECTORS["auth_password_input"], password)
        self.type_text(SELECTORS["signup_confirm_password_input"], password)
        self.click(SELECTORS["signup_submit_button"])
        return self

    def open_login(self, next_path: str | None = None):
        path = "/auth?mode=login"
        if next_path:
            path += f"&next={next_path}"
        self.open(path)
        self.wait_visible(SELECTORS["auth_email_input"])
        return self

    def login(self, email: str, password: str):
        self.type_text(SELECTORS["auth_email_input"], email)
        self.type_text(SELECTORS["auth_password_input"], password)
        self.click(SELECTORS["login_submit_button"])
        return self

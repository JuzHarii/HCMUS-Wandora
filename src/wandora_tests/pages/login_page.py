"""
login_page.py
--------------
Everything about logging in lives here. Tests just call:

    LoginPage(driver).login_as("editor")

and never see an email/password field directly.
"""

from config import SELECTORS, ACCOUNTS
from pages.base_page import BasePage


class LoginPage(BasePage):
    def open_login(self):
        self.open("/login")
        return self

    def login_as(self, role: str):
        """
        role: one of "owner", "editor", "viewer", "second_editor"
        (see config.ACCOUNTS). Logs in through the real login form --
        no token injection, no backend shortcuts.
        """
        account = ACCOUNTS[role]
        self.open_login()
        self.type_text(SELECTORS["login_email_input"], account["email"])
        self.type_text(SELECTORS["login_password_input"], account["password"])
        self.click(SELECTORS["login_submit_button"])
        return self

    def is_on_login_page(self) -> bool:
        return self.is_present(SELECTORS["login_page_marker"], timeout=5)

    def logout(self):
        """Clear session so the next test starts as a guest. Only touches
        browser storage/cookies -- still no backend calls."""
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")
        return self

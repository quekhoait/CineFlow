from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from tests.selenium.pages import AbstractPages

class HomePage(AbstractPages):
    # Form login
    LOGIN_CARD = (By.ID, "master-card")
    AUTH_MODAL = (By.ID, "auth")
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_SUBMIT = (By.ID, "submit-login")
    CLOSE_AUTH = (By.ID, "close-auth")
    BTN_GOOGLE = (By.CSS_SELECTOR, "#google-login button")
    LOGOUT_BTN = (By.ID, "logout")
    MASTER_CARD_NAV = (By.ID, "master-card")

    TAB_REGIS = (By.ID, "regis")
    USERNAME_FIELD = (By.NAME, "username")
    FULLNAME_FIELD = (By.NAME, "full_name")
    EMAIL_FIELD = (By.NAME, "email")
    OTP_FIELD = (By.NAME, "otp")
    PASSWORD_FIELD = (By.NAME, "password")
    RE_PASSWORD_FIELD = (By.NAME, "re-password")
    SUBMIT_BTN = (By.ID, "regis-btn")
    OTP_BTN = (By.ID, "otp-btn")

    def open_home(self):
        self.open(self.host)

    def open_login_form(self):
        self.click(*self.LOGIN_CARD)

    def open_regis_form(self):
        self.click(*self.TAB_REGIS)

    def login_email_flow(self, email, password):
        self.typing(*self.EMAIL_INPUT, text=email)
        self.typing(*self.PASSWORD_INPUT, text=password)
        self.click(*self.LOGIN_SUBMIT)

    def hover_avatar(self):
        avatar_element = self.find(*self.MASTER_CARD_NAV)
        actions = ActionChains(self.driver)
        actions.move_to_element(avatar_element).perform()
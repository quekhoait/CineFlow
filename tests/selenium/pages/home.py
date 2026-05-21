from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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

    SLIDER_NOW_SHOWING = (By.ID, "slider-1")
    SLIDER_UPCOMING = (By.ID, "slider-2")
    MOVIE_ITEMS_NOW_SHOWING = (By.CSS_SELECTOR, "#slider-1 .flex-none")
    MOVIE_ITEMS_UPCOMING = (By.CSS_SELECTOR, "#slider-2 .flex-none")

    SCROLL_LEFT_BTN_1 = (By.CSS_SELECTOR, "button[onclick*=\"scrollSlider('slider-1', -300)\"]")
    SCROLL_RIGHT_BTN_1 = (By.CSS_SELECTOR, "button[onclick*=\"scrollSlider('slider-1', 300)\"]")

    SCROLL_LEFT_BTN_2 = (By.CSS_SELECTOR, "button[onclick*=\"scrollSlider('slider-2', -300)\"]")
    SCROLL_RIGHT_BTN_2 = (By.CSS_SELECTOR, "button[onclick*=\"scrollSlider('slider-2', 300)\"]")

    NAV_HOME = (By.CSS_SELECTOR, "#master-nav a[href='/']")
    NAV_SCHEDULE = (By.CSS_SELECTOR, "#master-nav a[href='/schedule']")
    NAV_FILM = (By.CSS_SELECTOR, "#master-nav a[href='/film']")

    PROFILE_BTN = (By.CSS_SELECTOR, "a[href='/profile']")
    HISTORY_BTN = (By.CSS_SELECTOR, "a[href='/history']")

    def open_home(self):
        self.open(self.host)

    def open_login_form(self):
        # Retry because header can re-render and first click may be swallowed.
        for _ in range(3):
            self.find(*self.LOGIN_CARD)
            self.driver.execute_script("arguments[0].click();", self.driver.find_element(*self.LOGIN_CARD))
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d: "hidden" not in d.find_element(*self.AUTH_MODAL).get_attribute("class")
                )
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.EMAIL_INPUT))
                return
            except TimeoutException:
                continue
        raise TimeoutException("Auth modal did not open")

    def open_regis_form(self):
        self.open_login_form()
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(*self.TAB_REGIS))
        import time
        time.sleep(0.2)  # Give DOM time to swap login/regis form
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(self.USERNAME_FIELD))
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.USERNAME_FIELD))

    def login_email_flow(self, email, password):
        self.typing(*self.EMAIL_INPUT, text=email)
        self.typing(*self.PASSWORD_INPUT, text=password)
        self.click(*self.LOGIN_SUBMIT)

    def hover_avatar(self):
        avatar_element = self.find(*self.MASTER_CARD_NAV)
        actions = ActionChains(self.driver)
        actions.move_to_element(avatar_element).perform()

    def close_modal(self):
        self.click(*self.CLOSE_AUTH)

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.selenium.pages import AbstractPages


class TicketComponents(AbstractPages):
    STEP_TICKET = (By.ID, "step-ticket")
    TICKET = (By.ID, "ticket")
    QR_CODE = (By.ID, "ticket-qrcode")
    SAVE_BUTTON = (By.ID, "save-ticket")
    HISTORY_LIST = (By.ID, "history-list")
    HISTORY_SEARCH = (By.ID, "search-his")
    HISTORY_CARD = (By.CSS_SELECTOR, "#history-list [data-code]")
    CARD_STATUS = (By.CSS_SELECTOR, "[data-type]")
    CARD_CANCEL = (By.CSS_SELECTOR, ".btn-cancel:not([disabled])")
    CARD_PAY = (By.CSS_SELECTOR, ".btn-payment:not([disabled])")

    def open_ticket_step(self, booking_code):
        self.driver.execute_script("sessionStorage.setItem('code', arguments[0]); sessionStorage.removeItem('selectedShowId');", booking_code)
        self.open(f"{self.host.rstrip('/')}/booking")

    def wait_ticket_step(self, booking_code=None):
        self.wait.until(EC.presence_of_element_located(self.TICKET))
        self.wait.until(EC.presence_of_element_located(self.QR_CODE))
        if booking_code:
            self.wait.until(lambda d: booking_code in d.find_element(*self.TICKET).text)

    def qr_or_text_rendered(self, booking_code):
        container = self.find(*self.QR_CODE)
        has_qr = len(container.find_elements(By.CSS_SELECTOR, "img, canvas, svg")) > 0 or container.get_attribute("innerHTML").strip() != ""
        return has_qr or booking_code in self.find(*self.TICKET).text

    def open_history(self):
        self.open(f"{self.host.rstrip('/')}/history")

    def wait_history_loaded(self):
        self.wait.until(EC.presence_of_element_located(self.HISTORY_LIST))

    def card(self, booking_code):
        return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#history-list [data-code="{booking_code}"]')))

    def status_text(self, booking_code):
        return self.card(booking_code).find_element(*self.CARD_STATUS).text.strip()

    def card_text(self, booking_code):
        return self.card(booking_code).text.strip()

    def is_qr_rendered(self):
        container = self.find(*self.QR_CODE)
        return len(container.find_elements(By.CSS_SELECTOR, "img, canvas, svg")) > 0 or container.get_attribute("innerHTML").strip() != ""

    def click_cancel(self, booking_code):
        self.card(booking_code).find_element(*self.CARD_CANCEL).click()

    def click_pay(self, booking_code):
        self.card(booking_code).find_element(*self.CARD_PAY).click()



from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.selenium.pages import AbstractPages


class PaymentComponents(AbstractPages):
    STEP_PAYMENT = (By.ID, "step-payment")
    INVOICE_ITEMS = (By.ID, "invoice_items")
    FINAL_TOTAL = (By.ID, "final_total")
    INFO_USER = (By.ID, "info_user")
    INFO_FILM = (By.ID, "info_film")
    NEXT_PAYMENT_BUTTON = (By.ID, "btn_next_payment")
    PAY_BUTTON = (By.CSS_SELECTOR, "#btn_payment button")
    ALERT_BOX = (By.ID, "form_alert")
    ALERT_TITLE = (By.CSS_SELECTOR, "#alert_text p.font-bold")
    ALERT_MESSAGE = (By.CSS_SELECTOR, "#alert_text p:not(.font-bold)")
    TIMER = (By.ID, "timer")

    def wait_loaded(self):
        self.wait.until(EC.presence_of_element_located(self.INVOICE_ITEMS))
        self.wait.until(EC.visibility_of_element_located(self.FINAL_TOTAL))
        self.wait.until(EC.presence_of_element_located(self.INFO_FILM))

    def wait_for_invoice_total(self, expected_total):
        self.wait.until(lambda d: self.invoice_total() == expected_total)

    def invoice_total(self):
        text = self.find(*self.FINAL_TOTAL).text
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else 0

    def click_pay_now(self):
        button = self.wait.until(EC.presence_of_element_located(self.PAY_BUTTON))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", button)

    def pay_button_onclick(self):
        return self.wait.until(EC.presence_of_element_located(self.PAY_BUTTON)).get_attribute("onclick") or ""

    def wait_for_pay_binding(self, booking_code):
        self.wait.until(lambda d: booking_code in self.pay_button_onclick())

    def start_payment_for(self, booking_code):
        self.driver.execute_script("handleStartPayment(arguments[0]);", booking_code)

    def alert_title_text(self):
        return self.find(*self.ALERT_TITLE).text.strip()

    def alert_message_text(self):
        return self.find(*self.ALERT_MESSAGE).text.strip()

    def alert_class(self):
        return self.find(*self.ALERT_BOX).get_attribute("class")

    def timer_text(self):
        return self.find(*self.TIMER).text.strip()






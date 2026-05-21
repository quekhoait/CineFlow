import re

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.selenium.pages import AbstractPages


class BookingPage(AbstractPages):
    STEP_SEAT_SELECTION = (By.ID, "step-seat-selection")
    STEP_PAYMENT = (By.ID, "step-payment")
    STEP_TICKET = (By.ID, "step-ticket")
    BOOKING_SUMMARY = (By.ID, "booking_summary")
    SEAT_CONTAINER = (By.ID, "seat_container")
    SEAT_ITEMS = (By.CSS_SELECTOR, "#seat_container .seat-item")
    SELECTED_SEATS_TEXT = (By.ID, "selected_seats_list")
    TOTAL_PRICE = (By.ID, "total_price")
    CONTINUE_BUTTON = (By.ID, "btn_next_payment")
    INVOICE_ITEMS = (By.ID, "invoice_items")
    FINAL_TOTAL = (By.ID, "final_total")
    PAYMENT_BUTTONS = (By.ID, "btn_payment")
    ALERT_BOX = (By.ID, "form_alert")
    ALERT_TITLE = (By.CSS_SELECTOR, "#alert_text p.font-bold")
    ALERT_MESSAGE = (By.CSS_SELECTOR, "#alert_text p:not(.font-bold)")

    def open_booking(self):
        self.open(f"{self.host.rstrip('/')}/booking")

    def open_booking_for_show(self, show_id):
        self.driver.execute_script("sessionStorage.removeItem('code'); sessionStorage.setItem('selectedShowId', arguments[0]);", str(show_id))
        self.open_booking()

    def wait_for_booking_loaded(self):
        self.wait.until(EC.presence_of_element_located(self.SEAT_CONTAINER))
        self.wait.until(EC.presence_of_element_located(self.BOOKING_SUMMARY))
        self.wait.until(lambda d: len(d.find_elements(*self.SEAT_ITEMS)) > 0)

    def get_seat(self, seat_code):
        return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#seat_container .seat-item[data-code="{seat_code}"]')))

    def seat_classes(self, seat_code):
        return self.get_seat(seat_code).get_attribute("class")

    def seat_data(self, seat_code):
        seat = self.get_seat(seat_code)
        return {
            "booked": seat.get_attribute("data-booked"),
            "price": seat.get_attribute("data-price"),
            "type": seat.get_attribute("data-type"),
            "location": seat.get_attribute("data-location"),
            "classes": seat.get_attribute("class"),
        }

    def click_seat(self, seat_code):
        self.get_seat(seat_code).click()

    def get_selected_seats_text(self):
        return self.find(*self.SELECTED_SEATS_TEXT).text.strip()

    def get_total_price(self):
        text = self.find(*self.TOTAL_PRICE).text
        digits = re.sub(r"\D", "", text or "")
        return int(digits) if digits else 0

    def get_invoice_total(self):
        text = self.find(*self.FINAL_TOTAL).text
        digits = re.sub(r"\D", "", text or "")
        return int(digits) if digits else 0

    def click_continue(self):
        button = self.wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        try:
            button.click()
        except Exception:
            try:
                ActionChains(self.driver).move_to_element(button).click().perform()
            except Exception:
                self.driver.execute_script("arguments[0].click();", button)

    def alert_state(self):
        box = self.find(*self.ALERT_BOX)
        return {
            "classes": box.get_attribute("class"),
            "title": self.find(*self.ALERT_TITLE).text.strip(),
            "message": self.find(*self.ALERT_MESSAGE).text.strip(),
        }

    def current_step_hidden(self, step_id):
        return "hidden" in self.driver.find_element(By.ID, step_id).get_attribute("class")

    def current_step_visible(self, step_id):
        return "hidden" not in self.driver.find_element(By.ID, step_id).get_attribute("class")




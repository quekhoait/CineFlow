from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.selenium.pages import AbstractPages


class BookingComponents(AbstractPages):
    STEP_SEAT_SELECTION = (By.ID, "step-seat-selection")
    STEP_PAYMENT = (By.ID, "step-payment")
    STEP_TICKET = (By.ID, "step-ticket")
    BOOKING_SUMMARY = (By.ID, "booking_summary")
    SEAT_CONTAINER = (By.ID, "seat_container")
    SEAT_ITEMS = (By.CSS_SELECTOR, "#seat_container .seat-item")
    SELECTED_SEATS_TEXT = (By.ID, "selected_seats_list")
    TOTAL_PRICE = (By.ID, "total_price")
    CONTINUE_BUTTON = (By.ID, "btn_next_payment")
    ALERT_BOX = (By.ID, "form_alert")
    ALERT_MESSAGE = (By.CSS_SELECTOR, "#alert_text p:not(.font-bold)")

    def open_for_show(self, show_id):
        self.driver.execute_script("sessionStorage.removeItem('code'); sessionStorage.setItem('selectedShowId', arguments[0]);", str(show_id))
        self.open(f"{self.host.rstrip('/')}/booking")
        self.driver.execute_async_script("""
            const done = arguments[arguments.length - 1];
            import('/static/javascript/components/booking_components.js')
                .then(m => m.loadSeat())
                .then(done).catch(done);
        """)

    def wait_loaded(self):
        self.wait.until(EC.presence_of_element_located(self.SEAT_CONTAINER))
        self.wait.until(EC.presence_of_element_located(self.BOOKING_SUMMARY))
        self.wait.until(lambda d: len(d.find_elements(*self.SEAT_ITEMS)) > 0)

    def seat(self, seat_code):
        return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#seat_container .seat-item[data-code="{seat_code}"]')))

    def click_seat(self, seat_code):
        self.seat(seat_code).click()

    def click_seats(self, seat_codes):
        for seat_code in seat_codes:
            self.click_seat(seat_code)

    def total_price(self):
        text = self.find(*self.TOTAL_PRICE).text
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else 0

    def selected_seats_text(self):
        return self.find(*self.SELECTED_SEATS_TEXT).text.strip()

    def continue_booking(self):
        button = self.find(*self.CONTINUE_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", button)

    def click_continue(self):
        self.continue_booking()

    def alert_message(self):
        return self.find(*self.ALERT_MESSAGE).text.strip()

    def alert_class(self):
        return self.find(*self.ALERT_BOX).get_attribute("class")

    def step_visible(self, step_id):
        return "hidden" not in self.driver.find_element(By.ID, step_id).get_attribute("class")

    def step_hidden(self, step_id):
        return "hidden" in self.driver.find_element(By.ID, step_id).get_attribute("class")





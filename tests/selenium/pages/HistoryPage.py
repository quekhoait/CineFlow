from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from tests.selenium.pages import AbstractPages


class HistoryPage(AbstractPages):
    # Locators cho Đăng nhập
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), 'Đăng nhập')]")

    # Locators cho trang Lịch sử dựa trên file history.html và item_history.html
    SEARCH_INPUT = (By.ID, "search-his")
    HISTORY_CARDS = (By.CSS_SELECTOR, "#history-list > div[data-code]")
    STATUS_TEXT = (By.CSS_SELECTOR, "span[data-type]")

    # Nút bấm linh hoạt (Tìm theo text hiển thị)
    CANCEL_BUTTON = (By.XPATH, ".//button[contains(text(), 'Hủy vé') or contains(text(), 'Hủy')]")
    PAY_BUTTON = (By.XPATH, ".//button[contains(text(), 'Thanh toán')]")
    PAGINATION_CONTROLS = (By.ID, "pagination-controls")

    # Nút xác nhận hủy vé (Thích ứng linh hoạt với form_alert.html)
    CONFIRM_ALERT_BTN = (By.XPATH,
                         "//button[contains(text(), 'Xác nhận') or contains(text(), 'Đồng ý') or contains(text(), 'Có')]")

    def navigate_to_and_login(self, base_url):
        # 1. Mở trang chủ
        self.open(base_url + "/")
        time.sleep(2)

        # 2. Mở Popup Đăng nhập
        try:
            btn_user_menu = self.driver.find_element(By.ID, "master-card")
            self.driver.execute_script("arguments[0].click();", btn_user_menu)
        except:
            btn_user_menu = self.driver.find_element(By.XPATH,
                                                     "//*[contains(text(), 'Đăng Nhập') or contains(text(), 'Đăng nhập')]")
            self.driver.execute_script("arguments[0].click();", btn_user_menu)

        time.sleep(1.5)

        # 3. Điền form và NHẤN ENTER (Fix lỗi không bấm nút xanh)
        self.find(*self.EMAIL_INPUT).send_keys("admin@cineflow.me")

        password_field = self.find(*self.PASSWORD_INPUT)
        password_field.send_keys("Abc123@")

        # Thêm thư viện Keys nếu file chưa có: from selenium.webdriver.common.keys import Keys
        # Nhấn Enter thẳng trên ô Password để submit form thay vì click nút
        password_field.send_keys(Keys.ENTER)

        time.sleep(3)  # Tăng thời gian chờ lên 3s vì mạng Production có thể load API chậm hơn Local

        # 4. Chuyển sang History
        self.open(base_url + "/history")

    def search_action(self, text, press_enter=False):
        search_field = self.find(*self.SEARCH_INPUT)
        search_field.clear()
        search_field.send_keys(text)
        if press_enter:
            search_field.send_keys(Keys.ENTER)

    def count_results(self):
        try:
            return len(self.finds(*self.HISTORY_CARDS))
        except:
            return 0

    def clear_search_input(self):
        search_input = self.find(*self.SEARCH_INPUT)
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.BACKSPACE)

    def get_all_history_cards(self):
        try:
            return self.finds(*self.HISTORY_CARDS)
        except:
            return []

    def get_ticket_status(self, card_element):
        status_element = card_element.find_element(*self.STATUS_TEXT)
        return status_element.text.strip()

    def has_cancel_button(self, card_element):
        try:
            return len(card_element.find_elements(*self.CANCEL_BUTTON)) > 0
        except:
            return False

    def click_pay_button(self, card_element):
        btn = card_element.find_element(*self.PAY_BUTTON)
        # Dùng JS Click để tránh bị cản bởi lớp opacity decoraterbg3.png
        self.driver.execute_script("arguments[0].click();", btn)

    def click_cancel_button(self, card_element):
        btn = card_element.find_element(*self.CANCEL_BUTTON)
        self.driver.execute_script("arguments[0].click();", btn)

    def confirm_cancel_dialog(self):
        try:
            # Ưu tiên tìm nút Xác nhận trong popup HTML (form_alert.html)
            confirm_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.CONFIRM_ALERT_BTN)
            )
            self.driver.execute_script("arguments[0].click();", confirm_btn)
        except:
            # Fallback nếu dùng hàm alert/confirm() mặc định của Javascript
            alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert.accept()

    def get_pagination_text(self):
        try:
            return self.find(*self.PAGINATION_CONTROLS).text
        except:
            return ""
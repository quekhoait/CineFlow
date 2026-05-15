from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.selenium.page import AbstractPages  # Hãy chắc chắn đường dẫn import này chính xác trong dự án của bạn

class FilmPage(AbstractPages):
    # Định nghĩa các Locators dưới dạng Tuple (By, Value)
    SEARCH_INPUT = (By.ID, 'master-search')
    FILM_ITEM = (By.CSS_SELECTOR, '#list_film > div')
    BUTTON_DETAIL = (By.ID, "btn_detail_film")
    TITLE_FILM = (By.CSS_SELECTOR, '#film_description h1')
    LIST_DATE = (By.ID, 'date_film')
    LIST_CINEMAS = (By.ID, 'list-cinemas')
    SHOW_FILM = (By.CSS_SELECTOR, '#list-cinemas button')

    def navigate_to(self, base_url, route):
        target_url = base_url + route
        self.open(target_url)

    def search_action(self, text, press_enter=False):
        # Tận dụng hàm find từ lớp cha và rải tuple bằng dấu *
        search_field = self.find(*self.SEARCH_INPUT)
        search_field.clear()
        search_field.send_keys(text)
        if press_enter:
            search_field.send_keys(Keys.ENTER)

    def count_results(self):
        try:
            # Dùng finds để đợi danh sách element tải xong
            elements = self.finds(*self.FILM_ITEM)
            return len(elements)
        except:
            return 0 # Trả về 0 nếu không tìm thấy kết quả nào thay vì văng lỗi

    def click_detail_film(self):
        self.click(*self.BUTTON_DETAIL)

    def check_detail_film(self):
        element = self.find(*self.TITLE_FILM)
        return element.text

    def clear_search_input(self):
        search_input = self.find(*self.SEARCH_INPUT)
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.BACKSPACE)

    def list_date_tab(self):
        return self.find(*self.LIST_DATE)

    def is_cinema_displayed(self):
        return self.find(*self.LIST_CINEMAS).is_displayed()

    def get_all_show_film(self):
        return self.finds(*self.SHOW_FILM)
import time

from selenium.webdriver.common.by import By
from tests.selenium.pages import AbstractPages


class SchedulePage(AbstractPages):
    LIST_BRANCH = (By.ID, 'branch_location')
    BUTTON_SELECT_BRANCH = (By.CSS_SELECTOR, '#branch_location button')

    NAV_DATE=(By.ID, 'date_picker')
    BUTTON_NAV_DATE=(By.CSS_SELECTOR, '#date_picker > button')

    ADDRESS_CINEMA = (By.CSS_SELECTOR, '#address_cinema > p')
    LIST_SCHEDULE = (By.CSS_SELECTOR, '#schedule-film')
    COUNT_FILM_SCHEDULE = (By.CSS_SELECTOR, '#schedule-film > div')
    BUTTON_SHOW_SCHEDULE = (By.CSS_SELECTOR, '#schedule-film button')

    FILM_TITLE = (By.CSS_SELECTOR, '#schedule-film h3')
    EMPTY_MESSAGE  =(By.CSS_SELECTOR, '#schedule-film > div > p')

    FILM_TITLE_SUMMARY = (By.CSS_SELECTOR, '#booking_summary h3')
    SHOW_TIME_SELECT = (By.CSS_SELECTOR, '#booking_summary  div.text-sm > p:nth-child(4)')

    MAP_SEATS = (By.CSS_SELECTOR, '#seat_container > div')


    def navigate_to(self, base_url, route):
        target_url = base_url + route
        self.open(target_url)

    def is_nav_date_displayed(self):
        return self.find(*self.NAV_DATE).is_displayed()

    def is_schedule_displayed(self):
        return self.find(*self.LIST_SCHEDULE).is_displayed()

    def get_showtime_buttons(self):
        return self.finds(*self.BUTTON_SHOW_SCHEDULE)

    def is_branch_cinema_displayed(self):
        return self.find(*self.LIST_BRANCH).is_displayed()

    def click_select_cinema(self, index):
        branches = self.finds(*self.BUTTON_SELECT_BRANCH)
        if len(branches) > index:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                branches[index]
            )
            time.sleep(0.2)
            button_text = branches[index].text
            branches[index].click()
            return button_text
        else:
            raise IndexError(f"Không tìm thấy chi nhánh tại vị trí index {index}")

    def click_select_date(self, index):
        dates = self.finds(*self.BUTTON_NAV_DATE)
        if len(dates) > index:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dates[index])
            time.sleep(0.2)
            dates[index].click()
        else:
            raise IndexError(f"Không tìm thấy chi nhánh tại vị trí index {index}")

    def check_address_cinema(self):
        elements = self.finds(*self.ADDRESS_CINEMA)
        return [e.text for e in elements]

    def get_detailed_film_schedule(self):
        detailed_data = {}
        films = self.finds(*self.COUNT_FILM_SCHEDULE)
        for film in films:
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    film
                )
                time.sleep(2)
                title_element = film.find_element(*self.FILM_TITLE)
                film_name = title_element.text
                showtimes = film.find_elements(*self.BUTTON_SHOW_SCHEDULE)
                showtimes_count = len(showtimes)
                detailed_data[film_name] = showtimes_count
            except Exception as e:
                print(f"Lỗi khi đọc dữ liệu của một bộ phim: {e}")
                continue
        return detailed_data

    def is_schedule_empty(self):
        elements = self.finds(*self.EMPTY_MESSAGE)
        if not elements:
            return False
        return elements[0].is_displayed()

    def check_select_summary(self):
        elements = self.find(*self.FILM_TITLE_SUMMARY)
        show = self.find(*self.SHOW_TIME_SELECT)
        return elements.text, show.text

    def check_map_seats(self):
        return self.find(*self.MAP_SEATS).is_displayed()

    def check_type_seats(self, seat_element):
        return seat_element.get_attribute("data-type").strip()




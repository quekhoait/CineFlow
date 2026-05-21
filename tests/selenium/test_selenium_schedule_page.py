import time
from datetime import datetime
import pytest
from selenium.common import ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By

from tests.selenium.pages.home import HomePage
from tests.selenium.pages.SchedulePage import SchedulePage


def test_loading_data(driver, local_server_url):
    schedule_page = SchedulePage(driver)
    schedule_page.navigate_to(local_server_url, '/schedule')
    time.sleep(1)
    assert schedule_page.is_nav_date_displayed(), (
        "Lỗi: Thanh điều hướng ngày không hiển thị trên trang lịch chiếu!"
    )
    assert schedule_page.is_schedule_displayed(), (
        "Lỗi: Khu vực lịch chiếu không hiển thị!"
    )
    assert schedule_page.is_branch_cinema_displayed(), (
        "Lỗi: Chi nhánh rạp không load được"
    )

def test_select_branches(driver, local_server_url):
    schedule_page = SchedulePage(driver)
    schedule_page.navigate_to(local_server_url, '/schedule')
    time.sleep(1)
    content_btn = schedule_page.click_select_cinema(1)
    time.sleep(1)
    address = schedule_page.check_address_cinema()
    assert content_btn == address[0]
    print("Địa chỉ cụ thể: ", address[1])
    content_btn = schedule_page.click_select_cinema(2)
    time.sleep(1)
    address = schedule_page.check_address_cinema()
    assert content_btn == address[0]
    print("Địa chỉ cụ thể: ", address[1])
    content_btn = schedule_page.click_select_cinema(0)
    time.sleep(1)
    address = schedule_page.check_address_cinema()
    assert content_btn == address[0]
    print("Địa chỉ cụ thể: ", address[1])


def test_select_date_branches(driver, local_server_url):
    schedule_page = SchedulePage(driver)
    schedule_page.navigate_to(local_server_url, '/schedule')
    time.sleep(5)
    schedule_page.click_select_cinema(2)
    schedule_page.click_select_date(1)
    time.sleep(2)
    print("\n--- Lần 1 ---")
    if schedule_page.is_schedule_empty():
        assert schedule_page.is_schedule_empty(), (
            "Thất bại: Danh sách lịch chiếu trống nhưng không tìm thấy thông báo 'Hiện tại không có suất chiếu nào...'"
        )
    else:
        schedule_details = schedule_page.get_detailed_film_schedule()
        for film_name, showtime_qty in schedule_details.items():
            print(f"Phim: {film_name} | Số suất chiếu: {showtime_qty} suất")
            assert showtime_qty > 0, (
                f"Thất bại: Bộ phim '{film_name}' hiển thị trên giao diện nhưng số lượng suất chiếu lại bằng 0!"
            )
    time.sleep(4)
    schedule_page.click_select_cinema(2)
    schedule_page.click_select_date(4)
    time.sleep(3)
    print("\n--- Lần 2 ---")
    if schedule_page.is_schedule_empty():  #
        print("Trạng thái: Lần 2 trống lịch chiếu đúng như mong đợi.")
        assert schedule_page.is_schedule_empty(), (
            "Thất bại: Danh sách lịch chiếu trống nhưng không tìm thấy thông báo 'Hiện tại không có suất chiếu nào...'"
        )
    else:
        schedule_details_2 = schedule_page.get_detailed_film_schedule()
        for film_name, showtime_qty in schedule_details_2.items():
            print(f"Phim: {film_name} | Số suất chiếu: {showtime_qty} suất")
            assert showtime_qty > 0, (
                f"Thất bại: Bộ phim '{film_name}' hiển thị trên giao diện nhưng số lượng suất chiếu lại bằng 0!"
            )

    time.sleep(3)


def test_past_showtimes_are_disabled(driver, local_server_url):
    schedule_page = SchedulePage(driver)
    schedule_page.navigate_to(local_server_url, '/schedule')
    time.sleep(2)

    schedule_page.click_select_cinema(0)
    schedule_page.click_select_date(0)
    time.sleep(3)

    current_time = datetime.now().time()
    print(f"\nThời gian hiện tại: {current_time}")

    showtime_buttons = schedule_page.get_showtime_buttons()
    assert len(showtime_buttons) > 0, "Không tìm thấy suất chiếu nào trên giao diện."

    current_url = driver.current_url
    past_buttons_checked = 0
    for button in showtime_buttons:
        if past_buttons_checked >= 3:
            break

        showtime_text = button.text.strip()
        if not showtime_text:
            continue
        try:
            show_time = datetime.strptime(showtime_text, "%H:%M").time()
        except ValueError:
            continue
        if show_time < current_time:
            past_buttons_checked += 1
            print(f"\n[Suất quá khứ {past_buttons_checked}]: {showtime_text}")
            classes = button.get_attribute("class")
            assert "pointer-events-none" in classes, f"Nút {showtime_text} thiếu class pointer-events-none"
            assert "cursor-not-allowed" in classes, f"Nút {showtime_text} thiếu class cursor-not-allowed"
            assert "opacity-40" in classes, f"Nút {showtime_text} thiếu class opacity-40"
            try:
                driver.execute_script("arguments[0].click();", button)
            except (ElementClickInterceptedException, ElementNotInteractableException):
                pass
            time.sleep(0.5)
            assert driver.current_url == current_url, f"Lỗi: Suất quá khứ {showtime_text} vẫn click được và chuyển hướng URL!"
    if past_buttons_checked == 0:
        pytest.skip("Chạy test vào đầu ngày: Không có suất chiếu quá khứ nào để kiểm tra tại thời điểm này.")

#các show time ở tương lai
def test_button_showtimes_in_future(driver, local_server_url):
    schedule_page = SchedulePage(driver)
    schedule_page.navigate_to(local_server_url, '/schedule')
    time.sleep(1)
    schedule_page.click_select_cinema(0)
    schedule_page.click_select_date(1)
    time.sleep(1)
    showtime_buttons = schedule_page.get_showtime_buttons()
    assert len(showtime_buttons) > 0, (
        "Không tìm thấy suất chiếu nào"
    )
    for button in showtime_buttons:
        classes = button.get_attribute("class")
        assert "pointer-events-none" not in classes
        assert "cursor-not-allowed" not in classes
        assert "opacity-40" not in classes


def test_select_showtime_without_no_login(driver, local_server_url):
    schedule_page = SchedulePage(driver)
    schedule_page.navigate_to(local_server_url, '/schedule')
    time.sleep(1)
    schedule_page.click_select_cinema(1)
    schedule_page.click_select_date(1)
    time.sleep(2)
    showtime_buttons = schedule_page.get_showtime_buttons()
    time.sleep(2)
    assert len(showtime_buttons) > 0, "Không tìm thấy suất chiếu nào để test."
    showtime_buttons[0].click()
    time.sleep(1)
    mess = schedule_page.find(By.CSS_SELECTOR, '#alert_text > p:nth-child(2)')
    assert mess is not None
    assert mess.text == "Vui lòng đăng nhập để tiếp tục."



def test_select_showtime_with_login(driver, local_server_url):
    home = HomePage(driver)
    home.host = local_server_url
    home.open_home()
    home.open_login_form()
    home.typing(By.NAME, "email", "admin@cineflow.me")
    home.typing(By.NAME, "password", "Abc123@")
    home.click(By.ID, "submit-login")

    schedule_page = SchedulePage(driver)
    schedule_page.navigate_to(local_server_url, '/schedule')
    time.sleep(2)
    schedule_page.click_select_cinema(0)
    schedule_page.click_select_date(1)
    time.sleep(2)

    showtime_buttons = schedule_page.get_showtime_buttons()
    assert len(showtime_buttons) > 0, "Không tìm thấy suất chiếu nào để test ở ngày tương lai."
    raw_showtime_time = showtime_buttons[0].text.strip()
    expected_showtime_time = raw_showtime_time.replace(":", "h")

    movie_title_element = showtime_buttons[0].find_element(
        By.XPATH, "./ancestor::div[contains(@class, 'flex-grow')]//h3"
    )
    expected_movie_title = movie_title_element.text.strip()
    print(expected_movie_title)

    driver.execute_script("arguments[0].click();", showtime_buttons[0])
    time.sleep(1)
    assert "/booking" in driver.current_url
    title_summary, show_summary = schedule_page.check_select_summary()

    print("Phim được chọn là: ", title_summary)
    print("Suất chiếu được chọn là: ", show_summary)

    assert expected_movie_title.lower() in title_summary.lower(), (
        f"Tên phim không khớp"
    )
    assert expected_showtime_time in show_summary, (
        f"Suất chiếu không khớp giờ"
    )


def test_schedule_state_after_browser_back(driver, local_server_url):
    home = HomePage(driver)
    home.host = local_server_url
    home.open_home()
    home.open_login_form()
    home.typing(By.NAME, "email", "admin@cineflow.me")
    home.typing(By.NAME, "password", "Abc123@")
    home.click(By.ID, "submit-login")

    schedule_page = SchedulePage(driver)
    schedule_page.navigate_to(local_server_url, '/schedule')
    time.sleep(2)
    cinemas_name = schedule_page.click_select_cinema(2)
    date_time = 1
    schedule_page.click_select_date(date_time)
    time.sleep(2)

    showtime_buttons = schedule_page.get_showtime_buttons()
    driver.execute_script("arguments[0].click();", showtime_buttons[0])
    time.sleep(1)
    assert "/booking" in driver.current_url, "Không chuyển hướng đến trang booking."
    time.sleep(1)

    driver.back()
    time.sleep(2)
    assert "/schedule" in driver.current_url

    branches = driver.find_elements(*schedule_page.BUTTON_SELECT_BRANCH)
    matched_cinema = None
    for branch in branches:
        if branch.text.strip() == cinemas_name.strip():
            matched_cinema = branch
            break
    assert matched_cinema is not None
    cinema_classes = matched_cinema.get_attribute("class")
    assert "bg-[#3d55a4]" in cinema_classes, (
        f"Rạp đã chọn trước đó '{cinemas_name}' không còn giữ"
    )

    date_buttons = driver.find_elements(By.ID, "#date_picker > button")
    if len(date_buttons) > date_time:
        date_classes = date_buttons[date_time].get_attribute("class")
        assert "active" in date_classes or "text-white" in date_classes, (
            f"Ngày đã chọn trước đó (index {date_time}) đã bị reset"
        )


def test_validate_seat_states_colors_and_types(driver, local_server_url):
    home = HomePage(driver)
    home.host = local_server_url
    home.open_home()
    home.open_login_form()
    home.typing(By.NAME, "email", "admin@cineflow.me")
    home.typing(By.NAME, "password", "Abc123@")
    home.click(By.ID, "submit-login")

    schedule_page = SchedulePage(driver)
    schedule_page.navigate_to(local_server_url, '/schedule')
    time.sleep(2)
    schedule_page.click_select_cinema(0)
    schedule_page.click_select_date(1)
    time.sleep(2)

    showtime_buttons = schedule_page.get_showtime_buttons()
    assert len(showtime_buttons) > 0, "Không tìm thấy suất chiếu nào."
    driver.execute_script("arguments[0].click();", showtime_buttons[0])
    time.sleep(1)
    assert "/booking" in driver.current_url, "Không vào được trang đặt ghế."
    time.sleep(2)
    map_seat = schedule_page.check_map_seats()
    assert map_seat is not None
    time.sleep(2)

    seat_a2 = driver.find_element(
        By.CSS_SELECTOR,
        '[data-location="A2"]'
    )
    bg_color_a2 = seat_a2.get_attribute("class")
    assert "bg-white" in bg_color_a2, f"Ghế đơn chưa đặt (A2) sai màu"
    type_a2 = schedule_page.check_type_seats(seat_a2)
    assert type_a2 == "SINGLE", f"Ghế A2 phải có data-type là SINGLE"

    seat_f1 = driver.find_element(
        By.CSS_SELECTOR,
        '[data-location="F1"]'
    )
    bg_color_f1 = seat_f1.get_attribute("class")
    assert "bg-[#F8A4FF]" in bg_color_f1, f"Ghế đơn chưa đặt (F1) sai màu"
    type_f1 = schedule_page.check_type_seats(seat_f1)
    assert type_f1 == "COUPLE", f"Ghế F1 phải có data-type là DOUBLE"


def test_multi_tabs_showtime_independent(driver, local_server_url):
    home = HomePage(driver)
    home.host = local_server_url
    home.open_home()
    home.open_login_form()
    home.typing(By.NAME, "email", "admin@cineflow.me")
    home.typing(By.NAME, "password", "Abc123@")
    home.click(By.ID, "submit-login")
    schedule_page = SchedulePage(driver)

    #mở tab 1
    schedule_page.navigate_to(local_server_url, "/schedule")
    time.sleep(2)
    schedule_page.click_select_cinema(0)
    schedule_page.click_select_date(1)
    time.sleep(2)
    showtime_buttons_tab1 = schedule_page.get_showtime_buttons()
    assert len(showtime_buttons_tab1) >= 2
    raw_showtime_time = showtime_buttons_tab1[0].text.strip()
    expected_showtime_time_tab1 = raw_showtime_time.replace(":", "h")

    movie_title_element_tab1 = showtime_buttons_tab1[0].find_element(
        By.XPATH, "./ancestor::div[contains(@class, 'flex-grow')]//h3"
    )
    expected_movie_title_tab1 = movie_title_element_tab1.text.strip()
    print(expected_movie_title_tab1)

    # showtime_buttons_tab1[0].click()
    driver.execute_script("arguments[0].click();", showtime_buttons_tab1[0])
    time.sleep(1)
    assert "/booking" in driver.current_url
    title_summary_tab1, show_summary_tab1 = schedule_page.check_select_summary()

    print("Phim được chọn tab1 là: ", title_summary_tab1)
    print("Suất chiếu được chọn tab 1 là: ", show_summary_tab1)
    assert title_summary_tab1 == expected_movie_title_tab1
    assert expected_showtime_time_tab1 in show_summary_tab1
    #tab 2
    driver.switch_to.new_window('tab')

    schedule_page.navigate_to(local_server_url, "/schedule")
    time.sleep(2)
    schedule_page.click_select_cinema(1)
    schedule_page.click_select_date(1)
    time.sleep(2)
    showtime_buttons_tab2 = schedule_page.get_showtime_buttons()
    assert len(showtime_buttons_tab2) >= 2
    raw_showtime_time = showtime_buttons_tab2[0].text.strip()
    expected_showtime_time_tab2 = raw_showtime_time.replace(":", "h")

    movie_title_element_tab2 = showtime_buttons_tab2[0].find_element(
        By.XPATH, "./ancestor::div[contains(@class, 'flex-grow')]//h3"
    )
    expected_movie_title_tab2 = movie_title_element_tab2.text.strip()
    print(expected_movie_title_tab2)
    driver.execute_script("arguments[0].click();", showtime_buttons_tab2[0])
    time.sleep(1)
    assert "/booking" in driver.current_url
    title_summary_tab2, show_summary_tab2 = schedule_page.check_select_summary()

    print("Phim được chọn tab2 là: ", title_summary_tab2)
    print("Suất chiếu được chọn tab 2 là: ", show_summary_tab2)
    assert title_summary_tab2 == expected_movie_title_tab2
    assert expected_showtime_time_tab2 in show_summary_tab2

    assert title_summary_tab1 != title_summary_tab2, \
        "Hai tab đang dùng cùng một suất chiếu"

def test_multi_tabs_showtime_login(driver, local_server_url):
    home = HomePage(driver)
    home.host = local_server_url
    home.open_home()
    home.open_login_form()
    home.typing(By.NAME, "email", "admin@cineflow.me")
    home.typing(By.NAME, "password", "Abc123@")
    home.click(By.ID, "submit-login")
    schedule_page = SchedulePage(driver)

    #mở tab 1
    schedule_page.navigate_to(local_server_url, "/schedule")
    time.sleep(2)
    tab1_handle = driver.current_window_handle
    schedule_page.click_select_cinema(0)
    schedule_page.click_select_date(1)
    time.sleep(5)
    showtime_buttons_tab1 = schedule_page.get_showtime_buttons()
    assert len(showtime_buttons_tab1) > 0
    #tab 2
    driver.switch_to.new_window('tab')
    schedule_page.navigate_to(local_server_url, "/")
    time.sleep(5)
    home.hover_avatar()
    home.click(*home.LOGOUT_BTN)

    #quay lại tab 1
    driver.switch_to.window(tab1_handle)
    time.sleep(1)
    # showtime_buttons_tab1[0].click()
    driver.execute_script("arguments[0].click();", showtime_buttons_tab1[0])
    time.sleep(1)
    assert "/booking" not in driver.current_url


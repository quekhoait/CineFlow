import pytest
import time

from tests.selenium.page.FilmPage import FilmPage


@pytest.mark.parametrize(
    'start_url, query, need_enter, expected_behavior',
    [
        ('/', 'Lật Mặt 8: Vòng Xoáy', True,
         'Search từ trang khác - Cần Enter'),

        ('/film', 'Kung Fu Panda 5', False,
         'Search tại trang phim - Live Search'),

        ('/film', 'Lật Mặt 8: Mortal Kombat 2', False,
         'Search tại trang phim - Live Search'),

        ('/film', '', False,
         'Không nhập key -> hiện toàn bộ phim')
    ]
)
def test_search_logic(driver, local_server_url, start_url, query, need_enter, expected_behavior):
    film_page = FilmPage(driver)
    film_page.navigate_to(local_server_url, start_url)
    time.sleep(2)
    total_films = None
    if query == '':
        total_films = film_page.count_results()
    film_page.search_action(
        query,
        press_enter=need_enter
    )
    time.sleep(2)
    results_count = film_page.count_results()
    if query == '':
        assert results_count == total_films, (
            f"Fail: {expected_behavior}"
        )
    else:
        assert results_count > 0, (
            f"Fail: {expected_behavior}"
        )

def test_clear_search_restore_all_films(driver,local_server_url):
    film_page = FilmPage(driver)
    driver.get(local_server_url + "/film")
    time.sleep(1)
    total_films = film_page.count_results()
    film_page.search_action(
        "Kung Fu Panda 5",
        press_enter=False
    )
    time.sleep(2)
    filtered_count = film_page.count_results()
    assert filtered_count <= total_films
    film_page.clear_search_input()
    time.sleep(4)
    restored_count = film_page.count_results()
    assert restored_count == total_films

def test_search_detail_film(driver,local_server_url):
    film_page = FilmPage(driver)
    driver.get(local_server_url + "/film")
    time.sleep(1)
    film_page.search_action(
        "Kung Fu Panda 5",
        press_enter=False
    )
    time.sleep(1)
    filtered_count = film_page.count_results()
    assert filtered_count > 0
    film_page.click_detail_film()
    time.sleep(1)
    title = film_page.check_detail_film()
    assert title == "Kung Fu Panda 5", ()

def test_detail_with_showtimes(driver, local_server_url):
    film_page = FilmPage(driver)
    driver.get(local_server_url + "/film")
    time.sleep(1)
    film_page.search_action(
        "Kung Fu Panda 5",
        press_enter=False
    )
    time.sleep(2)
    film_page.click_detail_film()
    time.sleep(1)
    list_date_tab = film_page.list_date_tab()
    assert list_date_tab is not None
    is_cinema_displayed = film_page.is_cinema_displayed()
    assert is_cinema_displayed, "Lỗi: Không hiển thị danh sách rạp!"
    show_film = film_page.get_all_show_film()
    assert len(show_film) > 0, f"Lỗi: Phim có lịch nhưng không tìm thấy nút giờ chiếu nào!"
    print(f"Suất chiếu đầu tiên là: {show_film[0].text}")
    assert ":" in show_film[0].text

def test_detail_no_showtimes(driver, local_server_url):
    film_page = FilmPage(driver)
    driver.get(local_server_url + "/film")
    time.sleep(1)
    film_page.search_action(
        "Jurassic World: Rebirth",
        press_enter=False
    )
    time.sleep(1)
    film_page.click_detail_film()
    time.sleep(1)
    show_film = film_page.get_all_show_film()
    assert len(show_film) == 0


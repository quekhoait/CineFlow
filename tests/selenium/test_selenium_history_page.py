import threading
from wsgiref.simple_server import make_server

import pytest
import time
from selenium.webdriver.common.by import By

from tests.selenium.pages.HistoryPage import HistoryPage

@pytest.mark.parametrize(
    'query, need_enter, expected_behavior',
    [
        ('Fantastic', False, 'Search bằng tên phim - Live Search'),
        # ('BKC41979', False, 'Search bằng mã vé chính xác - Live Search'),
        ('MA_GIA_123', False, 'Search mã vé không tồn tại -> Trả về 0 kết quả'),
        ('', False, 'Không nhập key -> Khôi phục hiển thị toàn bộ lịch sử')
    ]
)
def test_search_history_logic(driver, local_server_url_v2, query, need_enter, expected_behavior):
    history_page = HistoryPage(driver)
    history_page.navigate_to_and_login(local_server_url_v2)
    time.sleep(2)

    total_history = history_page.count_results() if query == '' else None

    history_page.search_action(query, press_enter=need_enter)
    time.sleep(2)

    results_count = history_page.count_results()

    if query == '':
        assert results_count == total_history, f"Fail: {expected_behavior}"
    elif query == 'MA_GIA_123':
        assert results_count == 0, f"Fail: {expected_behavior}"
    else:
        assert results_count > 0, f"Fail: {expected_behavior}"


def test_ui_business_cancel_button(driver, local_server_url_v2):
    history_page = HistoryPage(driver)
    history_page.navigate_to_and_login(local_server_url_v2)
    time.sleep(2)

    cards = history_page.get_all_history_cards()
    if not cards:
        pytest.skip("Chưa có data lịch sử đặt vé để kiểm tra trạng thái nút Hủy")

    for card in cards:
        status = history_page.get_ticket_status(card)
        if status in ["Đã check-in", "Đã hủy", "Đã hủy giữ ghế"]:
            assert not history_page.has_cancel_button(card), f"Lỗi UI: Vé '{status}' vẫn hiển thị nút Hủy!"


def test_tc10_click_cancel_ticket(driver, local_server_url_v2):
    history_page = HistoryPage(driver)
    history_page.navigate_to_and_login(local_server_url_v2)
    time.sleep(2)

    cards = history_page.get_all_history_cards()
    card_to_cancel = next((card for card in cards if history_page.has_cancel_button(card)), None)

    if not card_to_cancel:
        pytest.skip("Không có vé nào đủ điều kiện Hủy để test TC_10")

    ticket_code = card_to_cancel.get_attribute("data-code")

    history_page.click_cancel_button(card_to_cancel)
    time.sleep(1)

    history_page.confirm_cancel_dialog()
    time.sleep(3)

    updated_card = driver.find_element(By.CSS_SELECTOR, f"div[data-code='{ticket_code}']")

    new_status = history_page.get_ticket_status(updated_card)
    assert new_status == "Đã hủy", f"Lỗi: Kỳ vọng 'Đã hủy' nhưng thực tế là '{new_status}'"
    assert not history_page.has_cancel_button(updated_card), "Lỗi: Đã hủy thành công nhưng nút Hủy vé vẫn hiển thị"


def test_tc11_click_payment_redirect(driver, local_server_url_v2):
    history_page = HistoryPage(driver)
    history_page.navigate_to_and_login(local_server_url_v2)
    time.sleep(2)

    cards = history_page.get_all_history_cards()
    card_to_pay = None

    for card in cards:
        try:
            card.find_element(*HistoryPage.PAY_BUTTON)
            card_to_pay = card
            break
        except:
            continue

    if not card_to_pay:
        pytest.skip("Không có vé nào đang chờ thanh toán để test TC_11")

    history_page.click_pay_button(card_to_pay)
    time.sleep(2)

    assert "/booking" in driver.current_url, f"Lỗi: Bấm Thanh toán nhưng hệ thống không chuyển sang trang booking. URL hiện tại: {driver.current_url}"


def test_tc12_pagination_display(driver, local_server_url_v2):
    history_page = HistoryPage(driver)
    history_page.navigate_to_and_login(local_server_url_v2)
    time.sleep(2)

    pagination_text = history_page.get_pagination_text()

    if not pagination_text:
        pytest.skip("Không tìm thấy thanh phân trang. Data chưa đủ để tạo trang mới.")

    assert "Trang" in pagination_text and "/" in pagination_text, f"Lỗi UI Phân trang: {pagination_text}"
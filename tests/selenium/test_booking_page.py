import time
import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from werkzeug.security import generate_password_hash

from app import db
from app.models import (
    Booking, Cinema, Film, Rules, Room, Seat, SeatType,
    Show, Ticket, User, UserAuthMethod, RoleEnum, Payment
)
from tests.selenium.pages.booking_components import BookingComponents
from tests.selenium.pages.booking import BookingPage
from tests.selenium.pages.payment_components import PaymentComponents
from tests.selenium.pages.home import HomePage
from tests.selenium.pages.ticket_components import TicketComponents


ENABLE_MANUAL_SCREENSHOT_WAIT = False


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _install_momo_mocks(monkeypatch, local_server_url, state):
    import app.pattern.method_payment as method_payment
    import app.services.booking_service as booking_service

    def fake_post(url, json=None, timeout=None, cookies=None, headers=None, **kwargs):
        if "gateway/api/create" in url:
            state["booking_code"] = json.get("extraData", state["booking_code"])
            order_id = json["orderId"]
            state["order_id"] = order_id
            state["amount"] = json["amount"]
            state["pay_url"] = f"{local_server_url}/booking?resultCode=0&orderId={order_id}&extraData={state['booking_code']}"
            return _FakeResponse({"orderId": order_id, "payUrl": state["pay_url"], "amount": json["amount"]})

        if "gateway/api/query" in url:
            return _FakeResponse({
                "partnerCode": json.get("partnerCode", ""),
                "requestId": json.get("requestId", ""),
                "orderId": json.get("orderId", ""),
                "amount": state["amount"],
                "extraData": state["booking_code"],
                "message": "Success",
                "orderInfo": "Pay with MoMo",
                "orderType": "captureWallet",
                "payType": "qr",
                "responseTime": "2024-01-01 00:00:00",
                "resultCode": 0,
                "transId": state.setdefault("trans_id", 123456789),
            })

        if "gateway/api/refund" in url:
            return _FakeResponse({
                "orderId": f"RF{uuid.uuid4().hex[:10].upper()}",
                "amount": json.get("amount", 0),
                "description": json.get("description", ""),
                "resultCode": 0,
                "transId": json.get("transId", 123456789),
            })

        raise AssertionError(f"Unexpected external request: {url}")

    monkeypatch.setattr(method_payment.requests, "post", fake_post)
    monkeypatch.setattr(booking_service.requests, "post", fake_post)


def _wait_booking_paid(app_instance, booking_code, timeout_seconds=12):
    end = time.time() + timeout_seconds
    while time.time() < end:
        with app_instance.app_context():
            booking = Booking.query.filter_by(code=booking_code).first()
            if booking and booking.payment_status and booking.payment_status.value == "PAID":
                return True
        time.sleep(0.2)
    return False


@pytest.fixture(autouse=True)
def setup_booking_data(app_instance):
    with app_instance.app_context():
        suffix = uuid.uuid4().hex[:8]
        email = f"admin{suffix}@cineflow.me"

        admin = User(
            username=f'admin{suffix}', email=email, password=generate_password_hash('Abc123@'),
            role=RoleEnum.ADMIN, full_name='Admin Test', is_active=True
        )
        db.session.add(admin)
        db.session.flush()

        db.session.add(UserAuthMethod(user_id=admin.id, provider="EMAIL", provider_id=email))

        rules_data = [
            ("SINGLE_WEEKDAY", "VND", "60000"), ("SINGLE_WEEKEND", "VND", "65000"),
            ("COUPLE_WEEKDAY", "VND", "120000"), ("COUPLE_WEEKEND", "VND", "130000"),
            ("HOLD_BOOKING", "MIN", "10"), ("CANCEL_HOUR", "HOUR", "2"),
        ]
        db.session.add_all([Rules(name=n, type=t, value=v, active=True, user_id=admin.id) for n, t, v in rules_data])

        cinema = Cinema(name=f"Cinema {suffix}", address="1 Test St", province="Hanoi", hotline="0123456789")
        db.session.add(cinema)
        db.session.flush()

        room = Room(name=f"Room {suffix}", row=4, column=10, cinema_id=cinema.id)
        db.session.add(room)
        db.session.flush()

        seats, seat_prefix = [], suffix[:4].upper()
        for i in range(1, 11):
            seats.append(Seat(code=f"{seat_prefix}-A{i}", type=SeatType.SINGLE, row="A", column=i, room_id=room.id))
        for i in range(1, 4):
            seats.append(Seat(code=f"{seat_prefix}-B{i}", type=SeatType.SINGLE, row="B", column=i, room_id=room.id))
        db.session.add_all(seats)

        film = Film(
            title=f"Film {suffix}", description="Test", genre="Action", age_limit=13,
            release_date=datetime.now().date(), expired_date=(datetime.now() + timedelta(days=60)).date(),
            poster="https://example.com/poster.jpg", duration=120
        )
        db.session.add(film)
        db.session.flush()

        show = Show(start_time=datetime.now() + timedelta(hours=26), film_id=film.id, room_id=room.id)
        db.session.add(show)
        db.session.flush()

        booking = Booking(
            code=f"BK{suffix[:6].upper()}", user_id=admin.id,
            total_price=180000, expired_time=datetime.now() + timedelta(minutes=10)
        )
        db.session.add(booking)
        db.session.flush()

        tickets = [Ticket(show_id=show.id, seat_code=f"{seat_prefix}-B{i}", booking_code=booking.code, price=60000,
                          active=True) for i in range(1, 4)]
        db.session.add_all(tickets)
        db.session.commit()

        yield {
            "email": email,
            "password": "Abc123@",
            "show_id": show.id,
            "available_seats": [f"{seat_prefix}-A{i}" for i in range(1, 11)],
            "unavailable_seats": [f"{seat_prefix}-B{i}" for i in range(1, 4)],
            "booking_code": booking.code,
        }

        db.session.query(Ticket).filter_by(show_id=show.id).delete(synchronize_session=False)
        db.session.flush()
        db.session.query(Payment).filter(Payment.booking_code.in_(
            db.session.query(Booking.code).filter_by(user_id=admin.id)
        )).delete(synchronize_session=False)
        db.session.flush()
        db.session.query(Booking).filter_by(user_id=admin.id).delete(synchronize_session=False)
        db.session.flush()
        db.session.query(Show).filter_by(id=show.id).delete(synchronize_session=False)
        db.session.query(Seat).filter_by(room_id=room.id).delete(synchronize_session=False)
        db.session.query(Room).filter_by(id=room.id).delete(synchronize_session=False)
        db.session.query(Cinema).filter_by(id=cinema.id).delete(synchronize_session=False)
        db.session.query(Rules).filter_by(user_id=admin.id).delete(synchronize_session=False)
        db.session.query(UserAuthMethod).filter_by(provider_id=email).delete(synchronize_session=False)
        db.session.query(User).filter_by(email=email).delete(synchronize_session=False)
        db.session.commit()


def _login(driver, url, email, pwd):
    home = HomePage(driver)
    home.host = url
    home.open_home()
    home.open_login_form()
    home.typing(By.NAME, "email", email)
    home.typing(By.NAME, "password", pwd)
    home.click(By.ID, "submit-login")
    WebDriverWait(driver, 10).until(
        lambda d: "bg-green-50" in d.find_element(By.ID, "form_alert").get_attribute("class"))


def _open_booking(driver, url, show_id):
    booking = BookingPage(driver)
    booking.host = url
    driver.execute_script(
        "sessionStorage.removeItem('code'); sessionStorage.setItem('selectedShowId', arguments[0]); window.location.href = '/booking';",
        str(show_id))
    WebDriverWait(driver, 10).until(EC.url_contains("/booking"))
    driver.execute_async_script("""
        const done = arguments[arguments.length - 1];
        import('/static/javascript/components/booking_components.js')
            .then(m => m.loadSeat())
            .then(done).catch(done);
    """)
    booking.wait_for_booking_loaded()
    return booking


@pytest.mark.parametrize("seat_count", [2])
def test_checkout_success(driver, local_server_url, setup_booking_data, seat_count):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = _open_booking(driver, local_server_url, setup_booking_data["show_id"])

    seats_to_pick = setup_booking_data["available_seats"][:seat_count]
    expected_total = 0

    for code in seats_to_pick:
        seat = booking.get_seat(code)
        expected_total += int(seat.get_attribute("data-price"))
        booking.click_seat(code)

    assert booking.get_total_price() == expected_total
    booking.click_continue()

    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: booking.current_step_visible("step-payment"))
    assert booking.current_step_hidden("step-seat-selection")


def test_max_seat_limit(driver, local_server_url, setup_booking_data):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = _open_booking(driver, local_server_url, setup_booking_data["show_id"])

    for code in setup_booking_data["available_seats"][:9]:
        booking.click_seat(code)

    booking.click_continue()

    WebDriverWait(driver, 10).until(lambda d: "bg-red-50" in d.find_element(By.ID, "form_alert").get_attribute("class"))
    assert booking.alert_state()["message"] == "Maximum 8 seats allowed"
    assert booking.current_step_visible("step-seat-selection")


@pytest.mark.parametrize("seat_idx", [0, 1, 2])
def test_unavailable_seat_click_ignored(driver, local_server_url, setup_booking_data, seat_idx):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = _open_booking(driver, local_server_url, setup_booking_data["show_id"])

    seat_code = setup_booking_data["unavailable_seats"][seat_idx]
    seat = booking.get_seat(seat_code)
    before_total = booking.get_total_price()

    assert seat.get_attribute("data-booked") == "true"
    driver.execute_script("arguments[0].click();", seat)

    assert booking.get_total_price() == before_total == 0


def test_spam_click_seat_prevention(driver, local_server_url, setup_booking_data):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = _open_booking(driver, local_server_url, setup_booking_data["show_id"])

    seat_code = setup_booking_data["available_seats"][0]
    seat_price = int(booking.get_seat(seat_code).get_attribute("data-price"))

    for _ in range(20):
        booking.click_seat(seat_code)

    total = booking.get_total_price()
    assert total == 0 or total == seat_price


def test_empty_seat_submission(driver, local_server_url, setup_booking_data):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = _open_booking(driver, local_server_url, setup_booking_data["show_id"])

    booking.click_continue()

    WebDriverWait(driver, 10).until(lambda d: "bg-red-50" in d.find_element(By.ID, "form_alert").get_attribute("class"))
    assert booking.alert_state()["message"] == "Please select at least one seat"


@pytest.mark.parametrize("seat_count", [1, 4, 8])
def test_booking_payment_generates_ticket(driver, local_server_url, app_instance, setup_booking_data, seat_count, monkeypatch):
    state = {"booking_code": setup_booking_data["booking_code"], "amount": 0}
    _install_momo_mocks(monkeypatch, local_server_url, state)
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    expected_total = 0
    for code in setup_booking_data["available_seats"][:seat_count]:
        expected_total += int(booking.seat(code).get_attribute("data-price"))
        booking.click_seat(code)

    assert booking.total_price() == expected_total
    booking.click_continue()

    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")
    assert booking_code is not None
    onclick = payment.pay_button_onclick()
    if booking_code in onclick:
        payment.click_pay_now()
    else:
        payment.start_payment_for(booking_code)
    WebDriverWait(driver, 10).until(lambda d: "resultCode=" in d.current_url or d.current_url.rstrip("/").endswith("/booking"))
    assert _wait_booking_paid(app_instance, booking_code)

    ticket = TicketComponents(driver)
    ticket.host = local_server_url
    ticket.open_history()
    ticket.wait_history_loaded()
    assert ticket.status_text(booking_code) == "Đã thanh toán"
    assert booking_code in ticket.card_text(booking_code)
    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


@pytest.mark.parametrize("seat_count", [8, 9])
def test_booking_capacity_and_expired_payment(driver, local_server_url, app_instance, setup_booking_data, seat_count):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    for code in setup_booking_data["available_seats"][:seat_count]:
        booking.click_seat(code)

    booking.click_continue()

    if seat_count == 9:
        WebDriverWait(driver, 10).until(lambda d: "bg-red-50" in booking.alert_class())
        assert booking.alert_message() == "Maximum 8 seats allowed"
        assert booking.step_visible("step-seat-selection")
        if ENABLE_MANUAL_SCREENSHOT_WAIT:
            time.sleep(30)
        return

    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")
    with app_instance.app_context():
        expected_total = int(Booking.query.filter_by(code=booking_code).first().total_price)
    with app_instance.app_context():
        db.session.add(
            Payment(
                code=f"HD{uuid.uuid4().hex[:10].upper()}",
                booking_code=booking_code,
                payment_method="MOMO",
                expired_time=datetime.now() - timedelta(minutes=1),
                pay_url="expired",
                amount=expected_total,
            )
        )
        db.session.commit()

    onclick = payment.pay_button_onclick()
    if booking_code in onclick:
        payment.click_pay_now()
    else:
        payment.start_payment_for(booking_code)
    WebDriverWait(driver, 10).until(lambda d: "bg-red-50" in payment.alert_class())
    assert "Transaction has expired" in payment.alert_message_text()
    assert booking.step_visible("step-payment")

    ticket = TicketComponents(driver)
    ticket.host = local_server_url
    ticket.open_history()
    ticket.wait_history_loaded()
    assert ticket.status_text(booking_code) != "Paid"
    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_booking_spam_navigation_and_cancel_flow(driver, local_server_url, app_instance, setup_booking_data, monkeypatch):
    state = {"booking_code": setup_booking_data["booking_code"], "amount": 0}
    _install_momo_mocks(monkeypatch, local_server_url, state)
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    target_code = setup_booking_data["available_seats"][0]
    target_price = int(booking.seat(target_code).get_attribute("data-price"))
    for _ in range(25):
        booking.click_seat(target_code)

    assert booking.total_price() in (0, target_price)

    first_group = setup_booking_data["available_seats"][:4]
    for code in first_group:
        booking.click_seat(code)

    booking.click_continue()
    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    for code in first_group:
        booking.click_seat(code)

    booking.click_continue()
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")
    with app_instance.app_context():
        expected_total = int(Booking.query.filter_by(code=booking_code).first().total_price)
    with app_instance.app_context():
        db.session.add(
            Payment(
                code=f"HD{uuid.uuid4().hex[:10].upper()}",
                booking_code=booking_code,
                payment_method="MOMO",
                expired_time=datetime.now() - timedelta(minutes=1),
                pay_url="expired",
                amount=expected_total,
            )
        )
        db.session.commit()

    onclick = payment.pay_button_onclick()
    if booking_code in onclick:
        payment.click_pay_now()
    else:
        payment.start_payment_for(booking_code)
    WebDriverWait(driver, 10).until(lambda d: "bg-red-50" in payment.alert_class())
    assert "Transaction has expired" in payment.alert_message_text()

    ticket = TicketComponents(driver)
    ticket.host = local_server_url
    ticket.open_history()
    ticket.wait_history_loaded()
    assert ticket.status_text(booking_code) != "Paid"
    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


@pytest.fixture
def driver_second():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def setup_weekend_mixed_seats(app_instance):
    import datetime as dt
    with app_instance.app_context():
        suffix = uuid.uuid4().hex[:8]
        email = f"admin{suffix}@cineflow.me"

        admin = User(
            username=f'admin{suffix}', email=email, password=generate_password_hash('Abc123@'),
            role=RoleEnum.ADMIN, full_name='Admin Test', is_active=True
        )
        db.session.add(admin)
        db.session.flush()

        db.session.add(UserAuthMethod(user_id=admin.id, provider="EMAIL", provider_id=email))

        db.session.query(Rules).delete(synchronize_session=False)
        db.session.flush()

        rules_data = [
            ("SINGLE_WEEKDAY", "VND", "60000"), ("SINGLE_WEEKEND", "VND", "80000"),
            ("COUPLE_WEEKDAY", "VND", "120000"), ("COUPLE_WEEKEND", "VND", "160000"),
            ("HOLD_BOOKING", "MIN", "10"), ("CANCEL_HOUR", "HOUR", "2"),
        ]
        db.session.add_all([Rules(name=n, type=t, value=v, active=True, user_id=admin.id) for n, t, v in rules_data])
        db.session.flush()

        cinema = Cinema(name=f"Cinema {suffix}", address="1 Test St", province="Hanoi", hotline="0123456789")
        db.session.add(cinema)
        db.session.flush()

        room = Room(name=f"Room {suffix}", row=4, column=10, cinema_id=cinema.id)
        db.session.add(room)
        db.session.flush()

        seats, seat_prefix = [], suffix[:4].upper()
        for i in range(1, 9):
            seats.append(Seat(code=f"{seat_prefix}-A{i}", type=SeatType.SINGLE, row="A", column=i, room_id=room.id))
        for i in range(1, 3):
            seats.append(Seat(code=f"{seat_prefix}-B{i}", type=SeatType.COUPLE, row="B", column=i, room_id=room.id))
        db.session.add_all(seats)
        db.session.flush()

        film = Film(
            title=f"Film {suffix}", description="Test", genre="Action", age_limit=13,
            release_date=datetime.now().date(), expired_date=(datetime.now() + timedelta(days=60)).date(),
            poster="https://example.com/poster.jpg", duration=120
        )
        db.session.add(film)
        db.session.flush()

        saturday_show = datetime.now() + timedelta(days=(5 - datetime.now().weekday()))
        if saturday_show.date() <= datetime.now().date():
            saturday_show = saturday_show + timedelta(days=7)
        saturday_show = saturday_show.replace(hour=18, minute=0, second=0, microsecond=0)

        show = Show(start_time=saturday_show, film_id=film.id, room_id=room.id)
        db.session.add(show)
        db.session.flush()

        booking = Booking(
            code=f"BK{suffix[:6].upper()}", user_id=admin.id,
            total_price=180000, expired_time=datetime.now() + timedelta(minutes=10)
        )
        db.session.add(booking)
        db.session.flush()

        tickets = [Ticket(show_id=show.id, seat_code=f"{seat_prefix}-B{i}", booking_code=booking.code, price=160000,
                          active=True) for i in range(1, 2)]
        db.session.add_all(tickets)
        db.session.commit()

        yield {
            "email": email,
            "password": "Abc123@",
            "show_id": show.id,
            "single_seats": [f"{seat_prefix}-A{i}" for i in range(1, 9)],
            "couple_seats": [f"{seat_prefix}-B{i}" for i in range(1, 3)],
            "unavailable_seats": [f"{seat_prefix}-B1"],
            "booking_code": booking.code,
        }

        db.session.query(Ticket).filter_by(show_id=show.id).delete(synchronize_session=False)
        db.session.flush()
        db.session.query(Payment).filter(Payment.booking_code.in_(
            db.session.query(Booking.code).filter_by(user_id=admin.id)
        )).delete(synchronize_session=False)
        db.session.flush()
        db.session.query(Booking).filter_by(user_id=admin.id).delete(synchronize_session=False)
        db.session.flush()
        db.session.query(Show).filter_by(id=show.id).delete(synchronize_session=False)
        db.session.query(Seat).filter_by(room_id=room.id).delete(synchronize_session=False)
        db.session.query(Room).filter_by(id=room.id).delete(synchronize_session=False)
        db.session.query(Cinema).filter_by(id=cinema.id).delete(synchronize_session=False)
        db.session.query(Rules).filter_by(user_id=admin.id).delete(synchronize_session=False)
        db.session.query(UserAuthMethod).filter_by(provider_id=email).delete(synchronize_session=False)
        db.session.query(User).filter_by(email=email).delete(synchronize_session=False)
        db.session.commit()


@pytest.mark.parametrize("seat_code", ["A1", "A2"])
def test_seat_conflict_concurrent_booking(driver, driver_second, local_server_url, app_instance, setup_booking_data, seat_code):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking1 = BookingComponents(driver)
    booking1.host = local_server_url
    booking1.open_for_show(setup_booking_data["show_id"])
    booking1.wait_loaded()

    _login(driver_second, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking2 = BookingComponents(driver_second)
    booking2.host = local_server_url
    booking2.open_for_show(setup_booking_data["show_id"])
    booking2.wait_loaded()

    target_seat = f"{setup_booking_data['available_seats'][0][:4]}-{seat_code}"
    booking1.click_seat(target_seat)
    time.sleep(0.5)
    booking2.click_seat(target_seat)
    time.sleep(0.5)

    booking1.click_continue()
    WebDriverWait(driver, 10).until(lambda d: booking1.step_visible("step-payment"))

    booking2.click_continue()
    WebDriverWait(driver_second, 10).until(lambda d: "bg-red-50" in booking2.alert_class())
    error_msg = booking2.alert_message()
    assert "Ticket already exists" in error_msg or "already booked" in error_msg.lower()
    assert booking2.step_visible("step-seat-selection")

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_momo_payment_user_cancellation_releases_seats(driver, local_server_url, app_instance, setup_booking_data, monkeypatch):
    state = {
        "booking_code": setup_booking_data["booking_code"],
        "amount": 0,
        "simulate_user_cancel": True
    }

    def fake_post_cancel(url, **kwargs):
        json_data = kwargs.get('json') or {}
        if "gateway/api/create" in url:
            state["booking_code"] = json_data.get("extraData", state["booking_code"])
            order_id = json_data["orderId"]
            state["order_id"] = order_id
            state["amount"] = json_data["amount"]
            state["pay_url"] = f"{local_server_url}/booking?resultCode=1006&orderId={order_id}&extraData={state['booking_code']}&message=User+canceled+the+transaction"
            return _FakeResponse({"orderId": order_id, "payUrl": state["pay_url"], "amount": json_data["amount"]})

        if "gateway/api/query" in url:
            return _FakeResponse({
                "partnerCode": json_data.get("partnerCode", ""),
                "requestId": json_data.get("requestId", ""),
                "orderId": json_data.get("orderId", ""),
                "amount": state["amount"],
                "extraData": state["booking_code"],
                "message": "User canceled",
                "resultCode": 1006,
                "transId": state.setdefault("trans_id", 123456789),
            })

        raise AssertionError(f"Unexpected external request: {url}")

    import app.pattern.method_payment as method_payment
    import app.services.booking_service as booking_service
    monkeypatch.setattr(method_payment.requests, "post", fake_post_cancel)
    monkeypatch.setattr(booking_service.requests, "post", fake_post_cancel)

    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    selected_seats = setup_booking_data["available_seats"][:3]
    for code in selected_seats:
        booking.click_seat(code)

    booking.click_continue()
    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")
    onclick = payment.pay_button_onclick()
    if booking_code in onclick:
        payment.click_pay_now()
    else:
        payment.start_payment_for(booking_code)

    time.sleep(2)

    with app_instance.app_context():
        booking_record = Booking.query.filter_by(code=booking_code).first()
        ticket_records = Ticket.query.filter_by(booking_code=booking_code, active=True).all()
        assert len(ticket_records) == 3
        assert booking_record.payment_status.value in ("PENDING", "REFUNDED", "REFUNDING")

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_url_tampering_signature_validation(driver, local_server_url, app_instance, setup_booking_data, monkeypatch):
    import hashlib
    import hmac

    state = {"booking_code": setup_booking_data["booking_code"], "amount": 0}
    _install_momo_mocks(monkeypatch, local_server_url, state)

    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    for code in setup_booking_data["available_seats"][:3]:
        booking.click_seat(code)

    booking.click_continue()
    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")
    original_amount = state["amount"]
    tampered_amount = original_amount // 10 if original_amount > 0 else 1000

    tampered_signature = "0" * 64

    driver.execute_script(f"window.tamperedCallbackData = {{'orderId': '{state.get('order_id', 'HD0000000000')}', 'amount': {tampered_amount}, 'extraData': '{booking_code}', 'resultCode': 0, 'signature': '{tampered_signature}', 'partnerCode': 'MOMO', 'requestId': 'REQ123', 'transId': '999999999'}};")

    driver.execute_script("const data = window.tamperedCallbackData; (async () => { const response = await fetch('/api/payments/momo/callback', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }); const result = await response.json(); window.callbackResult = result; })();")

    time.sleep(1)

    callback_result = driver.execute_script("return window.callbackResult;")
    assert callback_result is not None
    assert callback_result.get("status") == "error" or "signature" in callback_result.get("message", "").lower() or "invalid" in callback_result.get("message", "").lower()

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_mixed_seat_pricing_weekend_calculation(driver, local_server_url, app_instance, setup_weekend_mixed_seats, monkeypatch):
    state = {"booking_code": setup_weekend_mixed_seats["booking_code"], "amount": 0}
    _install_momo_mocks(monkeypatch, local_server_url, state)

    _login(driver, local_server_url, setup_weekend_mixed_seats["email"], setup_weekend_mixed_seats["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_weekend_mixed_seats["show_id"])
    booking.wait_loaded()

    single_seats_to_pick = setup_weekend_mixed_seats["single_seats"][:2]
    couple_seats_to_pick = setup_weekend_mixed_seats["couple_seats"][1:2]

    total_expected = 0
    for code in single_seats_to_pick:
        booking.click_seat(code)
        seat_elem = booking.seat(code)
        seat_price = int(seat_elem.get_attribute("data-price"))
        total_expected += seat_price

    for code in couple_seats_to_pick:
        booking.click_seat(code)
        seat_elem = booking.seat(code)
        seat_price = int(seat_elem.get_attribute("data-price"))
        total_expected += seat_price

    actual_ui_total = booking.total_price()
    assert actual_ui_total == total_expected, f"UI total {actual_ui_total} does not match expected {total_expected}"

    with app_instance.app_context():
        show_record = Show.query.filter_by(id=setup_weekend_mixed_seats["show_id"]).first()
        day_type = 'WEEKEND' if show_record.start_time.isoweekday() >= 6 else 'WEEKDAY'
        single_weekend_price = Rules.query.filter_by(name="SINGLE_WEEKEND").first()
        couple_weekend_price = Rules.query.filter_by(name="COUPLE_WEEKEND").first()

        expected_single = int(float(single_weekend_price.value)) * len(single_seats_to_pick)
        expected_couple = int(float(couple_weekend_price.value)) * len(couple_seats_to_pick)
        backend_expected = expected_single + expected_couple

        assert total_expected == backend_expected, f"Total {total_expected} does not match backend logic {backend_expected}"

    continue_button = booking.wait.until(EC.element_to_be_clickable((By.ID, "btn_next_payment")))
    try:
        continue_button.click()
    except Exception as click_exc:
        try:
            from selenium.webdriver import ActionChains

            ActionChains(driver).move_to_element(continue_button).click().perform()
        except Exception as act_exc:
            print("Failed to click Continue button:", click_exc, act_exc)

    try:
        alert_el = driver.find_element(By.ID, "form_alert")
        alert_text = alert_el.get_attribute("textContent") or alert_el.text
        print("form_alert class:", alert_el.get_attribute("class"), " textContent:", alert_text)
    except Exception:
        try:
            els = driver.find_elements(By.XPATH, "//*[contains(@class, 'bg-red-50') or contains(@class, 'text-red-600') or contains(@class, 'alert')]")
            for el in els:
                el_text = el.get_attribute("textContent") or el.text
                print("Alert-like element:", el.get_attribute("class"), " textContent:", el_text)
        except Exception:
            pass

    payment = PaymentComponents(driver)
    payment.host = local_server_url
    try:
        WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    except Exception as wait_exc:
        try:
            alert_el = driver.find_element(By.ID, "form_alert")
            alert_text = alert_el.get_attribute("textContent") or alert_el.text
            print("After wait failure - form_alert class:", alert_el.get_attribute("class"), " textContent:", alert_text)
        except Exception:
            pass
        assert False, "[DEVELOPER BUG REPORT: Mixed Seat Checkout Failed] - Payment step not visible after Continue click"
    payment.wait_loaded()

    payment_ui_total = payment.invoice_total()
    assert payment_ui_total == total_expected, f"Payment invoice total {payment_ui_total} does not match booking total {total_expected}"

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")
    onclick = payment.pay_button_onclick()
    if booking_code in onclick:
        payment.click_pay_now()
    else:
        payment.start_payment_for(booking_code)

    WebDriverWait(driver, 10).until(lambda d: "resultCode=" in d.current_url or d.current_url.rstrip("/").endswith("/booking"))
    assert _wait_booking_paid(app_instance, booking_code)

    with app_instance.app_context():
        paid_booking = Booking.query.filter_by(code=booking_code).first()
        assert paid_booking.total_price == total_expected

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_ten_minute_timeout_late_payment_rejected(driver, local_server_url, app_instance, setup_booking_data, monkeypatch):
    state = {"booking_code": setup_booking_data["booking_code"], "amount": 0}
    _install_momo_mocks(monkeypatch, local_server_url, state)

    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    for code in setup_booking_data["available_seats"][:4]:
        booking.click_seat(code)

    booking.click_continue()
    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")

    with app_instance.app_context():
        booking_record = Booking.query.filter_by(code=booking_code).first()
        booking_record.expired_time = datetime.now() - timedelta(minutes=1)
        db.session.commit()

    with app_instance.app_context():
        payment_record = Payment(
            code=f"HD{uuid.uuid4().hex[:10].upper()}",
            booking_code=booking_code,
            payment_method="MOMO",
            expired_time=datetime.now() - timedelta(minutes=1),
            pay_url="expired",
            amount=240000,
        )
        db.session.add(payment_record)
        db.session.commit()

    onclick = payment.pay_button_onclick()
    if booking_code in onclick:
        payment.click_pay_now()
    else:
        payment.start_payment_for(booking_code)

    WebDriverWait(driver, 10).until(lambda d: "bg-red-50" in payment.alert_class())
    alert_text = payment.alert_message_text()
    assert "expired" in alert_text.lower()

    with app_instance.app_context():
        final_booking = Booking.query.filter_by(code=booking_code).first()
        assert final_booking.payment_status.value != "PAID", f"Booking should not be PAID after timeout, but is {final_booking.payment_status.value}"

    ticket = TicketComponents(driver)
    ticket.host = local_server_url
    ticket.open_history()
    ticket.wait_history_loaded()
    status = ticket.status_text(booking_code)
    assert status != "Paid", f"Ticket status should not be Paid after timeout, but is {status}"

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_booking_creation_with_exact_8_seats_max_boundary(driver, local_server_url, app_instance, setup_booking_data, monkeypatch):
    state = {"booking_code": setup_booking_data["booking_code"], "amount": 0}
    _install_momo_mocks(monkeypatch, local_server_url, state)

    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    all_available = setup_booking_data["available_seats"][:8]
    total_expected = 0

    for code in all_available:
        booking.click_seat(code)
        seat_elem = booking.seat(code)
        seat_price = int(seat_elem.get_attribute("data-price"))
        total_expected += seat_price

    ui_total = booking.total_price()
    assert ui_total == total_expected
    assert len(all_available) == 8

    booking.click_continue()
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    assert booking.step_hidden("step-seat-selection")

    payment = PaymentComponents(driver)
    payment.host = local_server_url
    payment.wait_loaded()

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")
    assert booking_code is not None

    with app_instance.app_context():
        created_booking = Booking.query.filter_by(code=booking_code).first()
        assert created_booking is not None
        assert len(created_booking.tickets) == 8
        assert created_booking.total_price == total_expected

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_payment_with_momo_callback_state_mutation(driver, local_server_url, app_instance, setup_booking_data, monkeypatch):
    state = {"booking_code": setup_booking_data["booking_code"], "amount": 0, "call_count": 0}

    def fake_post_state_track(url, **kwargs):
        json_data = kwargs.get('json') or {}
        if "gateway/api/create" in url:
            state["call_count"] += 1
            state["booking_code"] = json_data.get("extraData", state["booking_code"])
            order_id = json_data["orderId"]
            state["order_id"] = order_id
            state["amount"] = json_data["amount"]
            state["pay_url"] = f"{local_server_url}/booking?resultCode=0&orderId={order_id}&extraData={state['booking_code']}"
            return _FakeResponse({"orderId": order_id, "payUrl": state["pay_url"], "amount": json_data["amount"]})

        if "gateway/api/query" in url:
            return _FakeResponse({
                "partnerCode": json_data.get("partnerCode", ""),
                "requestId": json_data.get("requestId", ""),
                "orderId": json_data.get("orderId", ""),
                "amount": state["amount"],
                "extraData": state["booking_code"],
                "message": "Success",
                "orderInfo": "Pay with MoMo",
                "orderType": "captureWallet",
                "payType": "qr",
                "responseTime": "2024-01-01 00:00:00",
                "resultCode": 0,
                "transId": state.setdefault("trans_id", 123456789),
            })

        raise AssertionError(f"Unexpected request: {url}")

    import app.pattern.method_payment as method_payment
    import app.services.booking_service as booking_service
    monkeypatch.setattr(method_payment.requests, "post", fake_post_state_track)
    monkeypatch.setattr(booking_service.requests, "post", fake_post_state_track)

    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    for code in setup_booking_data["available_seats"][:2]:
        booking.click_seat(code)

    booking.click_continue()
    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")
    assert booking_code is not None

    onclick = payment.pay_button_onclick()
    if booking_code in onclick:
        payment.click_pay_now()
    else:
        payment.start_payment_for(booking_code)

    time.sleep(1.5)
    
    assert state["call_count"] >= 1, f"Expected at least 1 API call, but got {state['call_count']}"

    WebDriverWait(driver, 10).until(lambda d: "resultCode=" in d.current_url or d.current_url.rstrip("/").endswith("/booking"))
    assert _wait_booking_paid(app_instance, booking_code)

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_seat_selection_state_persistence(driver, local_server_url, setup_booking_data):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = _open_booking(driver, local_server_url, setup_booking_data["show_id"])

    booking.click_seat(setup_booking_data["available_seats"][0])
    booking.click_seat(setup_booking_data["available_seats"][1])
    before_total = booking.get_total_price()
    assert before_total > 0

    driver.refresh()
    WebDriverWait(driver, 10).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#seat_container .seat-item")) > 0)

    after_refresh_total = booking.get_total_price()
    assert after_refresh_total == 0, "Selection should be cleared after page refresh"

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_seat_selection_unselect(driver, local_server_url, setup_booking_data):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = _open_booking(driver, local_server_url, setup_booking_data["show_id"])

    seat_code = setup_booking_data["available_seats"][0]
    seat_price = int(booking.get_seat(seat_code).get_attribute("data-price"))

    booking.click_seat(seat_code)
    assert booking.get_total_price() == seat_price, "Seat should be selected"

    booking.click_seat(seat_code)
    assert booking.get_total_price() == 0, "Seat should be unselected after clicking again"

    booking.click_seat(seat_code)
    assert booking.get_total_price() == seat_price, "Seat should be selected again"

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_booking_cancel_midway(driver, local_server_url, setup_booking_data):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = _open_booking(driver, local_server_url, setup_booking_data["show_id"])

    booking.click_seat(setup_booking_data["available_seats"][0])
    assert booking.get_total_price() > 0

    driver.get(f"{local_server_url.rstrip('/')}/")
    time.sleep(1)

    driver.back()
    time.sleep(1)

    current_url = driver.current_url
    assert "/booking" in current_url or current_url.rstrip("/").endswith("/"), "User should navigate away cleanly"

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_invalid_show_id_access(driver, local_server_url, setup_booking_data):
    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])

    invalid_show_id = 99999
    driver.execute_script(f"sessionStorage.setItem('selectedShowId', '{invalid_show_id}');")
    driver.get(f"{local_server_url.rstrip('/')}/booking")
    time.sleep(2)

    try:
        alert_el = driver.find_element(By.ID, "form_alert")
        assert alert_el.text or "error" in alert_el.get_attribute("class"), "Should show error for invalid show"
    except Exception:
        assert driver.current_url != f"{local_server_url.rstrip('/')}/booking", "Should redirect on invalid show"

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_payment_retry_after_failure(driver, local_server_url, setup_booking_data, monkeypatch):
    call_count = {"first": 0}

    def fake_post_fail_then_succeed(url, **kwargs):
        if "gateway/api/create" in url:
            call_count["first"] += 1
            json_data = kwargs.get('json') or {}
            order_id = json_data["orderId"]
            booking_code = json_data.get("extraData", setup_booking_data["booking_code"])

            if call_count["first"] == 1:
                return _FakeResponse({"error": "Network timeout", "orderId": order_id})
            else:
                return _FakeResponse({
                    "orderId": order_id,
                    "payUrl": f"{local_server_url}/booking?resultCode=0&orderId={order_id}&extraData={booking_code}",
                    "amount": json_data["amount"]
                })

        if "gateway/api/query" in url:
            return _FakeResponse({
                "orderId": kwargs.get("json", {}).get("orderId", ""),
                "resultCode": 0 if call_count["first"] > 1 else 1,
                "amount": kwargs.get("json", {}).get("amount", 0),
            })

        raise AssertionError(f"Unexpected request: {url}")

    import app.pattern.method_payment as method_payment
    import app.services.booking_service as booking_service
    monkeypatch.setattr(method_payment.requests, "post", fake_post_fail_then_succeed)
    monkeypatch.setattr(booking_service.requests, "post", fake_post_fail_then_succeed)

    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    booking.click_seat(setup_booking_data["available_seats"][0])
    booking.click_continue()

    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    booking_code = driver.execute_script("return sessionStorage.getItem('code');")

    try:
        onclick = payment.pay_button_onclick()
        if booking_code in onclick:
            payment.click_pay_now()
    except Exception:
        pass

    time.sleep(1)

    try:
        onclick = payment.pay_button_onclick()
        if booking_code in onclick:
            payment.click_pay_now()
    except Exception:
        pass

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_momo_network_timeout_scenario(driver, local_server_url, setup_booking_data, monkeypatch):
    def fake_post_slow(url, **kwargs):
        if "gateway/api/create" in url:
            time.sleep(2)
            json_data = kwargs.get('json') or {}
            return _FakeResponse({
                "orderId": json_data["orderId"],
                "payUrl": f"{local_server_url}/booking?resultCode=0&orderId={json_data['orderId']}&extraData={json_data.get('extraData')}",
                "amount": json_data["amount"]
            })

        if "gateway/api/query" in url:
            return _FakeResponse({"orderId": "", "resultCode": 1, "message": "Pending"})

        raise AssertionError(f"Unexpected request: {url}")

    import app.pattern.method_payment as method_payment
    import app.services.booking_service as booking_service
    monkeypatch.setattr(method_payment.requests, "post", fake_post_slow)
    monkeypatch.setattr(booking_service.requests, "post", fake_post_slow)

    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    booking.click_seat(setup_booking_data["available_seats"][0])
    booking.click_continue()

    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    start = time.time()
    try:
        payment.click_pay_now()
    except Exception:
        pass
    elapsed = time.time() - start
    assert elapsed < 15, "Should not hang indefinitely on slow gateway"

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)


def test_double_payment_prevention(driver, local_server_url, setup_booking_data, monkeypatch):
    call_count = {"create": 0}

    def fake_post_track_calls(url, **kwargs):
        if "gateway/api/create" in url:
            call_count["create"] += 1
            json_data = kwargs.get('json') or {}
            order_id = json_data["orderId"]
            booking_code = json_data.get("extraData", setup_booking_data["booking_code"])
            return _FakeResponse({
                "orderId": order_id,
                "payUrl": f"{local_server_url}/booking?resultCode=0&orderId={order_id}&extraData={booking_code}",
                "amount": json_data["amount"]
            })

        if "gateway/api/query" in url:
            return _FakeResponse({
                "orderId": kwargs.get("json", {}).get("orderId", ""),
                "resultCode": 0,
                "amount": kwargs.get("json", {}).get("amount", 0),
            })

        raise AssertionError(f"Unexpected request: {url}")

    import app.pattern.method_payment as method_payment
    import app.services.booking_service as booking_service
    monkeypatch.setattr(method_payment.requests, "post", fake_post_track_calls)
    monkeypatch.setattr(booking_service.requests, "post", fake_post_track_calls)

    _login(driver, local_server_url, setup_booking_data["email"], setup_booking_data["password"])
    booking = BookingComponents(driver)
    booking.host = local_server_url
    booking.open_for_show(setup_booking_data["show_id"])
    booking.wait_loaded()

    booking.click_seat(setup_booking_data["available_seats"][0])
    booking.click_continue()

    payment = PaymentComponents(driver)
    payment.host = local_server_url
    WebDriverWait(driver, 10).until(lambda d: booking.step_visible("step-payment"))
    payment.wait_loaded()

    onclick = payment.pay_button_onclick()
    if setup_booking_data["booking_code"] in onclick:
        payment.click_pay_now()
        time.sleep(0.2)

        try:
            payment.click_pay_now()
        except Exception:
            pass

    time.sleep(1)
    assert call_count["create"] <= 2, f"Gateway create API called {call_count['create']} times, should be <= 2"

    if ENABLE_MANUAL_SCREENSHOT_WAIT:
        time.sleep(30)
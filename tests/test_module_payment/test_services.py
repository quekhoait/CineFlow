from datetime import datetime, timedelta, date, time
from app.dto.payment_dto import PaymentRequest, MomoPaymentCallbackRequest
from app.models import Booking, Payment, PaymentStatus, BookingPaymentStatus, Ticket, PaymentType, Show, Film
from app.services import payment_service
import pytest
from marshmallow import ValidationError
from app import db
from app.utils.errors import TransactionComplete, NotFoundError, PaymentsError, UnauthorizedError, NoPaymentsMethod, \
    RefundedPaymentsError, NoPaymentsError


@pytest.fixture(autouse=True)
def app_context():
    from app import create_app
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture(autouse=True)
def client(app_context):
    return app_context.test_client()


# ================== FILM ==================
@pytest.fixture(autouse=True)
def sample_films(app_context):
    today = date.today()

    films = [
        # --- PHIM 1: Đang chiếu (còn lâu mới hết) ---
        Film(
            id=1,
            title="Cuộc Chiến Đa Vũ Trụ",
            description="Một bộ phim hành động viễn tưởng đỉnh cao.",
            genre="Hành Động, Viễn Tưởng",
            age_limit=13,
            release_date=today - timedelta(days=10),
            expired_date=today + timedelta(days=20),
            poster="poster_multiverse.jpg",
            duration=120
        ),

        # --- PHIM 2: Đang chiếu (sắp hết hạn) ---
        Film(
            id=2,
            title="Hài Kịch Cuối Tuần",
            description="Những tình huống dở khóc dở cười.",
            genre="Hài Hước",
            age_limit=16,
            release_date=today - timedelta(days=30),
            expired_date=today + timedelta(days=2),
            poster="poster_comedy.jpg",
            duration=95
        ),

        # --- PHIM 3: Sắp chiếu ---
        Film(
            id=3,
            title="Thám Tử Lừng Danh 2026",
            description="Phim trinh thám kịch tính.",
            genre="Trinh Thám",
            age_limit=18,
            release_date=today + timedelta(days=10),
            expired_date=today + timedelta(days=40),
            poster="poster_detective.jpg",
            duration=110
        ),

        # --- PHIM 4: Đã hết hạn ---
        Film(
            id=4,
            title="Ký Ức Đã Qua",
            description="Phim tình cảm lãng mạn.",
            genre="Tình Cảm",
            age_limit=13,
            release_date=today - timedelta(days=60),
            expired_date=today - timedelta(days=5),
            poster="poster_memory.jpg",
            duration=105
        ),

        # --- PHIM 5: Vừa mới chiếu hôm nay ---
        Film(
            id=5,
            title="Ngày Đầu Ra Mắt",
            description="Phim mới công chiếu hôm nay.",
            genre="Drama",
            age_limit=13,
            release_date=today,
            expired_date=today + timedelta(days=15),
            poster="poster_new.jpg",
            duration=100
        ),

        # --- PHIM 6: Sắp hết hạn ngay hôm nay ---
        Film(
            id=6,
            title="Suất Cuối Cùng",
            description="Chỉ còn chiếu hôm nay.",
            genre="Kinh Dị",
            age_limit=18,
            release_date=today - timedelta(days=20),
            expired_date=today,
            poster="poster_lastday.jpg",
            duration=90
        ),

        # --- PHIM 7: Chưa công bố (release = expired) ---
        Film(
            id=7,
            title="Phim Bí Ẩn",
            description="Chưa rõ thông tin.",
            genre="Mystery",
            age_limit=16,
            release_date=today + timedelta(days=5),
            expired_date=today + timedelta(days=5),
            poster="poster_secret.jpg",
            duration=100
        )
    ]

    db.session.add_all(films)
    db.session.commit()


# ================== BOOKING ==================
@pytest.fixture(autouse=True)
def sample_bookings(app_context):
    now = datetime.now()

    bookings = [
        # VALID
        Booking(
            code="BK_PAID_0",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=5),
            expired_time=now + timedelta(minutes=10)
        ),

        Booking(
            code="BK_PAID_2",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=5),
            expired_time=now + timedelta(minutes=10)
        ),

        # ĐÃ THANH TOÁN
        Booking(
            code="BK_PAID_3",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(minutes=5),
            expired_time=now + timedelta(minutes=10)
        ),

        # ĐÃ REFUND
        Booking(
            code="BK_PAID_4",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="REFUNDED",
            created_at=now - timedelta(minutes=5),
            expired_time=now + timedelta(minutes=10)
        ),

        # EXPIRED
        Booking(
            code="BK_EXPIRED",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=30),
            expired_time=now - timedelta(minutes=5)
        ),

        # SUCCESS
        Booking(
            code="BK_SUCCESS",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(hours=1),
            expired_time=now - timedelta(minutes=45)
        ),

        # REFUND VALID
        Booking(
            code="BK_REFUND_VALID",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(minutes=30),
            expired_time=now + timedelta(hours=5)
        ),

        # REFUND TOO LATE
        Booking(
            code="BK_REFUND_TOO_LATE",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(hours=5),
            expired_time=now - timedelta(hours=1)
        ),
        Booking(
            code="BK_NEW",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now,
            expired_time=now + timedelta(minutes=10)
        )
    ]

    db.session.add_all(bookings)
    db.session.commit()
    return bookings


# ================== PAYMENT ==================
@pytest.fixture(autouse=True)
def sample_payments(app_context):
    now = datetime.now()

    payments = [
        # SUCCESS
        Payment(
            code="PAY_BK1",
            booking_code="BK_PAID_1",
            payment_method="momo",
            amount=50000,
            status=PaymentStatus.PENDING,
            type=PaymentType.PAYMENT,
            expired_time=now + timedelta(minutes=10),
            pay_url="https://momo.vn/test"
        ),
        Payment(
            code="PAY_BK2",
            booking_code="BK_PAID_2",
            payment_method="momo",
            amount=50000,
            status=PaymentStatus.PENDING,
            type=PaymentType.PAYMENT,
            expired_time=now - timedelta(minutes=15),
            pay_url="https://momo.vn/test"
        ),

        Payment(
            code="PAY_BK3",
            booking_code="BK_PAID_3",
            payment_method="momo",
            transaction_id="TX456",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT,
            expired_time=now + timedelta(days=1)
        ),

        # REFUND
        Payment(
            code="PAY_BK4",
            booking_code="BK_PAID_4",
            payment_method="momo",
            transaction_id="TX789",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.REFUND,
            expired_time=now - timedelta(days=1)
        ),

        # EXPIRED PAYMENT
        Payment(
            code="PAY_OLD",
            booking_code="BK_SUCCESS",
            payment_method="momo",
            transaction_id="TX000",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT,
            expired_time=now - timedelta(minutes=10)
        ),

        # REFUND VALID
        Payment(
            code="PAY_REFUND_1",
            booking_code="BK_REFUND_VALID",
            payment_method="momo",
            transaction_id="TX999",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT,
            expired_time=now + timedelta(days=1)
        ),

        # REFUND TOO LATE
        Payment(
            code="PAY_REFUND_2",
            booking_code="BK_REFUND_TOO_LATE",
            payment_method="momo",
            transaction_id="TX888",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT,
            expired_time=now - timedelta(hours=5)
        ),
    ]

    db.session.add_all(payments)
    db.session.commit()
    return payments


# ================== SHOW ==================
@pytest.fixture(autouse=True)
def sample_shows(app_context):
    today = date.today()
    now = datetime.now()
    shows = [
        Show(
            id=1,
            start_time=datetime.combine(today, time(10, 0)),
            film_id=1,
            room_id=1
        ),
        Show(
            id=2,
            start_time=now + timedelta(hours=1),
            film_id=1,
            room_id=1
        )
    ]

    db.session.add_all(shows)
    db.session.commit()


# ================== TICKET ==================
@pytest.fixture(autouse=True)
def sample_tickets(app_context):
    tickets = [
        Ticket(show_id=1, seat_code="A1", booking_code="BK_PAID_0", price=50000, active=True),
        Ticket(show_id=1, seat_code="A1", booking_code="BK_PAID_1", price=50000, active=True),
        Ticket(show_id=2, seat_code="A2", booking_code="BK_PAID_2", price=50000, active=True),
        Ticket(show_id=1, seat_code="A3", booking_code="BK_PAID_3", price=50000, active=True),
        Ticket(show_id=1, seat_code="A4", booking_code="BK_SUCCESS", price=50000, active=True),
    ]

    db.session.add_all(tickets)
    db.session.commit()


@pytest.fixture
def logged_in_user(mocker):
    mocker.patch('app.services.payment_service.get_jwt_identity', return_value=4)
    return 4


def test_logic_create_payment_success(logged_in_user, mocker):
    # chỉ mock strategy thôi
    mock_strategy = mocker.Mock()
    mock_strategy.create.return_value = {
        "payUrl": "https://momo.vn/pay/success"
    }
    mocker.patch(
        'app.pattern.method_payment.PaymentContext.get_strategy',
        return_value=mock_strategy
    )
    payload = {
        "booking_code": "BK_PAID_0",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    res = payment_service.create(data)
    assert "payUrl" in res


def test_logic_create_payment_success_repeat(logged_in_user, mocker):
    mock_payment = mocker.Mock()
    mock_payment.status = PaymentStatus.PENDING
    mock_payment.expired_time = datetime.now() + timedelta(minutes=15)

    mock_payment.booking_code = "BK_PAID_0"
    mock_payment.pay_url = "https://momo.vn/pay/success"
    mocker.patch(
        'app.repository.payment_repo.get_payment_by_booking_code',
        return_value=mock_payment
    )

    # Mock booking_repo (trả về bất cứ thứ gì vì luồng này không dùng tới booking nhiều)
    mocker.patch(
        'app.repository.booking_repo.get_basic_booking_by_code',
        return_value=mocker.Mock()
    )
    payload = {
        "booking_code": "BK_PAID_0",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    res = payment_service.create(data)
    assert "payUrl" in res


# thanh toán lại thanh toán hết hanj
def test_create_payment_existing_expired_payment(mocker, logged_in_user):
    mock_strategy = mocker.Mock()
    mock_strategy.create.return_value = {
        "payUrl": "https://momo.vn/pay/pld"
    }
    mocker.patch(
        'app.pattern.method_payment.PaymentContext.get_strategy',
        return_value=mock_strategy
    )

    payload = PaymentRequest().load({
        "booking_code": "BK_PAID_2",
        "method": "momo"
    })

    with pytest.raises(PaymentsError) as excinfo:
        payment_service.create(payload)

    assert "Transaction has expired" in excinfo.value.message


# #Test logic booking đã thanh toán ròi mà thanh toán tiếp
def test_logic_create_payment_expired(logged_in_user):
    payload = {
        "booking_code": "BK_PAID_3",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(PaymentsError) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "This booking has already been paid."


# #
# # # #Không tìm thấy booking
def test_logic_create_momo_payment_by_not_booking(logged_in_user):
    payload = {
        "booking_code": "BK_HHHHHH",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(NotFoundError) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "Not found booking in your booking list"


#

# Dữ liệu đầu vào bị trống
@pytest.mark.parametrize("payload, expected_msg", [
    ({}, "Missing data for required field"),
    ({"method": "momo"}, "Missing data for required field"),
    ({"booking_code": "BK_PAID_1"}, "Missing data for required field"),
])
def test_logic_create_momo_payment_missing_payload(payload, expected_msg, logged_in_user):
    with pytest.raises(ValidationError) as excinfo:
        data = PaymentRequest().load(payload)
        payment_service.create(data)
    errors = excinfo.value.messages
    for field, msgs in errors.items():
        assert "Missing data for required field." in msgs


# # # #test thanh toán đơn hàng của user 4 với tài khoản user 5 (cả 2 đều có tài khoản)
def test_logic_create_payment_wrong_owner(mocker):
    mocker.patch('app.services.payment_service.get_jwt_identity', return_value=5)
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(NotFoundError) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "Not found booking in your booking list"


# #
# # #Thanh toán khi chưa đăng nhập
def test_logic_create_payment_not_login(mocker):
    mocker.patch('app.services.payment_service.get_jwt_identity', return_value=None)
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(UnauthorizedError) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "Unauthorized"


# #
# # #Thanh toán vơí method ko hợp lệ
def test_logic_create_payment_invalid_method(logged_in_user, mocker):
    mocker.patch('app.services.payment_service.payment_repo.get_payment_by_booking_code', return_value=None)
    payload = {
        "booking_code": "BK_PAID_0",
        "method": "bitcoin",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(NoPaymentsMethod) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "Payment method current is not supported"


# #

def test_momo_callback_service_success(mocker):
    mocker.patch(
        'app.pattern.method_payment.MomoPaymentStrategy._create_signature',
        return_value="mocked_signature"
    )
    payload = {
        "partnerCode": "MOMO",
        "orderId": "PAY_BK3",
        "resultCode": 0,
        "amount": 50000,
        "transId": 123456789,
        "extraData": "BK_PAID_3",
        "signature": "mocked_signature"
    }
    payment_service.callback("momo", payload)
    db.session.commit()
    booking = Booking.query.filter_by(code="BK_PAID_3").first()
    assert booking is not None
    assert booking.payment_status == BookingPaymentStatus.PAID


# callback bị lôi
def test_momo_callback_service_error(mocker):
    mock_update = mocker.patch('app.services.payment_service.payment_repo.update_payment_result_momo')
    mocker.patch(
        'app.pattern.method_payment.MomoPaymentStrategy._create_signature',
        return_value="mocked_signature"
    )
    mock_update.side_effect = Exception("Database connection failed")
    with pytest.raises(Exception) as excinfo:
        payment_service.callback("momo", {
            "partnerCode": "MOMO",
            "orderId": "PAY_BK2",
            "resultCode": 0,
            "amount": 50000,
            "transId": 123456789,
            "extraData": "BK_PAID_2",
            "signature": "mocked_signature"
        })
    assert "Database connection failed" in str(excinfo.value)


#
#
def test_momo_rollback_callback_service_error(mocker):
    mocker.patch('app.pattern.method_payment.MomoPaymentStrategy.callback', side_effect=Exception("Database Error"))
    mock_rollback = mocker.patch.object(db.session, 'rollback')
    data = {"orderId": "PAY_BK1"}
    with pytest.raises(Exception) as excinfo:
        payment_service.callback("momo", data)
    assert str(excinfo.value) == "Database Error"
    mock_rollback.assert_called_once()


#
def test_momo_transaction_success(logged_in_user):
    payload = {
        "partnerCode": "MOMO",
        "orderId": "PAY_BK3",
        "extraData": "BK_PAID_3",
        "resultCode": 0,
        "amount": 50000,
        "transId": "123456789"
    }
    payment_service.transaction("momo", payload)
    db.session.commit()
    booking = Booking.query.filter_by(code="BK_PAID_3").first()
    payment = Payment.query.filter_by(code="PAY_BK3").first()
    assert booking is not None
    assert booking.payment_status == BookingPaymentStatus.PAID
    assert payment.status == PaymentStatus.SUCCESS


#
def test_transaction_commits_on_success(logged_in_user, mocker):
    payload = {"resultCode": 0, "message": "Success"}
    mocker.patch('app.pattern.method_payment.MomoPaymentStrategy.transaction', return_value=payload)
    mock_commit = mocker.patch.object(db.session, 'commit')
    data = {"orderId": "PAY_BK1"}
    result = payment_service.transaction("momo", data)
    assert result.get('resultCode') == 0
    mock_commit.assert_called_once()


def test_transaction_rollbacks_on_exception(logged_in_user, mocker):
    mocker.patch('app.pattern.method_payment.MomoPaymentStrategy.transaction', side_effect=Exception("Database Error"))
    mock_rollback = mocker.patch.object(db.session, 'rollback')
    data = {"orderId": "PAY_BK1"}
    with pytest.raises(Exception) as excinfo:
        payment_service.transaction("momo", data)
    assert str(excinfo.value) == "Database Error"
    mock_rollback.assert_called_once()


def test_refund_success(mocker, logged_in_user, sample_bookings):
    mocker.patch('app.services.payment_service.get_jwt_identity', return_value=4)
    booking = [b for b in sample_bookings if b.code == "BK_REFUND_TOO_LATE"][0]
    from app.models import BookingPaymentStatus
    booking.payment_status = BookingPaymentStatus.REFUNDING
    mocker.patch('app.repository.booking_repo.get_booking_by_code', return_value=booking)
    mocker.patch('app.pattern.method_payment.MomoPaymentStrategy.refund', return_value=0)
    mock_commit = mocker.patch.object(db.session, 'commit')
    payload = {"booking_code": "BK_REFUND_TOO_LATE", "method": "momo"}
    data = PaymentRequest().load(payload)
    payment_service.refund(data)
    assert booking.payment_status == BookingPaymentStatus.REFUNDED
    mock_commit.assert_called_once()


def test_refund_error_booking(logged_in_user):
    payload = {"booking_code": "BK_PAID_311", "method": "momo"}
    with pytest.raises(NotFoundError) as excinfo:
        data = PaymentRequest().load(payload)
        payment_service.refund(data)
    assert excinfo.value.message == "Booking not found!"


def test_refund_no_transaction_id(logged_in_user):
    now = datetime.now()
    show_far = Show(id=99, start_time=now + timedelta(hours=5), film_id=1, room_id=1)
    new_booking = Booking(code="BK_NO_PAYMENT_DATA",
                          user_id=logged_in_user,
                          status="CANCELED",
                          payment_status="REFUNDING",
                          total_price=50000,
                          )
    ticket = Ticket(show_id=99, seat_code="B2", booking_code="BK_NO_PAYMENT_DATA", price=50000, active=True)
    db.session.add(show_far)
    db.session.add(ticket)
    db.session.add(new_booking)
    db.session.commit()
    payload = {"booking_code": "BK_NO_PAYMENT_DATA", "method": "momo"}

    with pytest.raises(NoPaymentsError) as excinfo:
        data = PaymentRequest().load(payload)
        payment_service.refund(data)
    assert excinfo.value.message == "You don't have any payments"


def test_auth(mocker):
    mocker.patch(
        "app.services.payment_service.get_jwt_identity",
        return_value=None
    )
    payload = {"orderId": "BK_PAY", "method": "momo"}
    with pytest.raises(UnauthorizedError) as excinfo:
        payment_service.transaction("momo", payload)
    assert excinfo.value.message == "Unauthorized"


def test_refund_error_payment(logged_in_user):
    payload = {"booking_code": "BK_PAID_4", "method": "momo"}
    with pytest.raises(RefundedPaymentsError) as excinfo:
        data = PaymentRequest().load(payload)
        payment_service.refund(data)
    assert excinfo.value.message == "Refunded payments"


def test_refund_rollbacks_on_exception(logged_in_user, mocker, sample_bookings):
    mocker.patch('app.pattern.method_payment.MomoPaymentStrategy.refund', side_effect=Exception("Database Error"))
    mock_rollback = mocker.patch.object(db.session, 'rollback')

    mocker.patch('app.services.payment_service.get_jwt_identity', return_value=logged_in_user)
    booking = [b for b in sample_bookings if b.code == "BK_REFUND_VALID"][0]
    from app.models import BookingPaymentStatus  # (Nhớ import đúng đường dẫn model)
    booking.payment_status = BookingPaymentStatus.REFUNDING

    mocker.patch('app.services.payment_service.booking_repo.get_booking_by_code', return_value=booking)

    payload = {"booking_code": "BK_REFUND_VALID", "method": "momo"}
    data_payload = PaymentRequest().load(payload)

    with pytest.raises(Exception) as excinfo:
        payment_service.refund(data_payload)

    assert str(excinfo.value) == "Database Error"

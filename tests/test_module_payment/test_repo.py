from datetime import datetime, timedelta, date, time
from app.dto.payment_dto import PaymentRequest, MomoPaymentCallbackRequest
from app.models import Booking, Payment, PaymentStatus, BookingPaymentStatus, Ticket, PaymentType, Show, Film
from app.repository import payment_repo
import pytest
from marshmallow import ValidationError
from app import db
from app.utils.errors import PaymentsError, NotFoundError


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
            express_time=now + timedelta(minutes=10)
        ),

        Booking(
            code="BK_PAID_2",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=5),
            express_time=now + timedelta(minutes=10)
        ),

        # ĐÃ THANH TOÁN
        Booking(
            code="BK_PAID_3",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(minutes=5),
            express_time=now + timedelta(minutes=10)
        ),

        # ĐÃ REFUND
        Booking(
            code="BK_PAID_4",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="REFUNDED",
            created_at=now - timedelta(minutes=5),
            express_time=now + timedelta(minutes=10)
        ),

        # EXPIRED
        Booking(
            code="BK_EXPIRED",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=30),
            express_time=now - timedelta(minutes=5)
        ),

        # SUCCESS
        Booking(
            code="BK_SUCCESS",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(hours=1),
            express_time=now - timedelta(minutes=45)
        ),

        # REFUND VALID
        Booking(
            code="BK_REFUND_VALID",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(minutes=30),
            express_time=now + timedelta(hours=5)
        ),

        # REFUND TOO LATE
        Booking(
            code="BK_REFUND_TOO_LATE",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(hours=5),
            express_time=now - timedelta(hours=1)
        ),
        Booking(
            code="BK_NEW",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now,
            express_time=now + timedelta(minutes=10)
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



def test_create_new_payment_with_momo_success():
    target_booking = "BK_PAID_1"
    momo_data = {
        'orderId': 'MOMO_REQ_789',
        'payUrl': 'https://test-payment.momo.vn/v2/gateway/redirect/xxx',
        'amount': 50000
    }
    payment_repo.create_new_payment_with_momo(target_booking, momo_data)
    new_payment = db.session.query(Payment).filter_by(code='MOMO_REQ_789').first()
    assert new_payment is not None
    assert new_payment.booking_code == target_booking
    assert new_payment.payment_method == "MOMO"
    assert new_payment.amount == 50000
    assert new_payment.pay_url == momo_data['payUrl']
    expected_expiry = datetime.now() + timedelta(minutes=15)
    diff = abs((new_payment.expired_time - expected_expiry).total_seconds())
    assert diff < 2

#kiểm tra mối quan he
def test_create_payment_linking_integrity():
    target_code = "BK_PAID_3"
    momo_data = {
        'orderId': 'MOMO_CRIT_001',
        'payUrl': 'https://momo.vn/pay',
        'amount': 50000
    }
    payment_repo.create_new_payment_with_momo(target_code, momo_data)
    payment = db.session.query(Payment).filter_by(code='MOMO_CRIT_001').first()
    booking = db.session.query(Booking).filter_by(code=target_code).first()

    assert payment.booking_code == booking.code

#NẾU MOMO TRẢ THIEUS DỮ LIỆU
def test_create_payment_with_missing_data_fields():
    invalid_data = {
        'orderId': 'FAIL_001'
        # Thiếu payUrl và amount
    }
    with pytest.raises(KeyError):
        payment_repo.create_new_payment_with_momo("BK_ANY", invalid_data)


def test_update_payment_success():
    momo_update_data = {
        'orderId': 'PAY_BK3',
        'extraData': 'BK_PAID_3',
        'transId': 1111111,
        'amount': 50000,
        'resultCode': 0
    }
    payment_repo.update_payment_result_momo(momo_update_data)
    payment = db.session.query(Payment).filter_by(code='PAY_BK3').first()
    assert payment.status == PaymentStatus.SUCCESS
    assert payment.transaction_id == 1111111
    assert payment.booking.payment_status == BookingPaymentStatus.PAID

#momo báo lỗi, ko update dc
def test_update_payment_failed_from_momo():
    momo_update_data = {
        'orderId': 'PAY_BK3',
        'extraData': 'BK_PAID_3',
        'transId': 1111111,
        'amount': 50000,
        'resultCode': 9000
    }
    payment_repo.update_payment_result_momo(momo_update_data)
    payment = db.session.query(Payment).filter_by(code='PAY_BK3').first()
    assert payment.status == PaymentStatus.FAILED
    assert payment.booking.payment_status == BookingPaymentStatus.PENDING
#
# #update khi quá hạn
def test_update_payment_expired():
    expired_payment = Payment(
        code="PAY_BK999",
        booking_code="BK_EXPIRED",
        amount=50000,
        status=PaymentStatus.PENDING,
        expired_time=datetime.now() - timedelta(minutes=16)
    )
    db.session.add(expired_payment)
    db.session.commit()
    momo_update_data = {
        'orderId': 'PAY_BK999',
        'extraData': 'BK_EXPIRED',
        'transId': 1111111,
        'amount': 50000,
        'resultCode': 0
    }
    with pytest.raises(PaymentsError) as exc:
        payment_repo.update_payment_result_momo(momo_update_data)
    assert expired_payment.status == PaymentStatus.FAILED
    assert "Payment expired" in str(exc.value.message )

def test_update_payment_not_found():
    invalid_data = {
        'orderId': 'NON_EXISTENT',
        'extraData': 'BK_EXPIRED',
        'transId': '123',
        'resultCode': 0
    }
    with pytest.raises(NotFoundError):
        payment_repo.update_payment_result_momo(invalid_data)

def test_create_refund_result_momo_success():
    booking_code = "BK_PAID_1"
    momo_refund_data = {
        'orderId': 'REFUND_MOMO_123',
        'amount': 50000,
        'resultCode': 0
    }
    payment_repo.create_refund_result_momo(booking_code, momo_refund_data)
    refund_record = db.session.query(Payment).filter_by(code='REFUND_MOMO_123').first()
    assert refund_record is not None
    assert refund_record.booking_code == booking_code
    assert refund_record.amount == 50000
    assert refund_record.status == PaymentStatus.SUCCESS
    assert refund_record.type == PaymentType.REFUND
    assert refund_record.payment_method == "MOMO"


def test_create_refund_result_momo_failed():
    booking_code = "BK_PAID_1"
    momo_refund_data = {
        'orderId': 'REFUND_MOMO_456',
        'amount': 50000,
        'resultCode': 1001
    }
    payment_repo.create_refund_result_momo(booking_code, momo_refund_data)

    refund_record = db.session.query(Payment).filter_by(code='REFUND_MOMO_456').first()

    assert refund_record.status == PaymentStatus.FAILED
    assert refund_record.type == PaymentType.REFUND


def test_get_payment_by_booking_code_found():
    target_booking_code = "BK_PAID_1"
    result = payment_repo.get_payment_by_booking_code(target_booking_code)
    assert result is not None
    assert isinstance(result, Payment)
    assert result.booking_code == target_booking_code
    assert result.code == "PAY_BK1"


def test_get_payment_by_booking_code_not_found():
    non_existent_code = "RANDOM_CODE_999"
    result = payment_repo.get_payment_by_booking_code(non_existent_code)
    assert result is None


def test_get_payment_by_booking_code_integrity():
    target_code = "BK_SUCCESS"
    result = payment_repo.get_payment_by_booking_code(target_code)
    assert result.booking_code == target_code
    assert result.amount == 50000
    assert result.booking.code == target_code
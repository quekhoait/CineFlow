from datetime import timedelta, date
from app.api import api as api_blueprint
import pytest
from flask import Flask
from datetime import datetime, timedelta
from app import db
from app.models import *
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"


    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    JWTManager(app)

    app.register_blueprint(api_blueprint)

    db.init_app(app)

    return app

@pytest.fixture
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()


@pytest.fixture
def sample_bookings(test_session):
    now = datetime(2026, 4, 7, 19, 15, 0)
    bookings = [
        # --- NHÓM 1: CÒN HẠN THANH TOÁN (Valid) ---
        Booking(
            code="BK_PAID_1",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=5),
            express_time=now + timedelta(minutes=10)  # Còn 10 phút
        ),

        Booking(
            code="BK_PAID_2",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=5),
            express_time=now + timedelta(minutes=10)  # Còn 10 phút
        ),
#Đ thành toán xong xuôi, gọi callback
        Booking(
            code="BK_PAID_3",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(minutes=5),
            express_time=now + timedelta(minutes=10)  # Còn 10 phút
        ),

        Booking(
            code="BK_PAID_4",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="REFUNDED",
            created_at=now - timedelta(minutes=5),
            express_time=now + timedelta(minutes=10)  # Còn 10 phút
        ),

        # --- NHÓM 2: SÁT NÚT HẾT HẠN (Critical) ---
        Booking(
            code="BK_CRITICAL",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=14, seconds=50),
            express_time=now + timedelta(seconds=10)  # Chỉ còn 10 giây
        ),

        # --- NHÓM 3: ĐÃ QUÁ HẠN 15 PHÚT (Expired) ---
        # Điều kiện: express_time < now
        Booking(
            code="BK_EXPIRED",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=20),
            express_time=now - timedelta(minutes=5)  # Đã hết hạn 5 phút trước
        ),

        # --- NHÓM 4: ĐÃ THANH TOÁN RỒI (Already Paid) ---
        Booking(
            code="BK_SUCCESS",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(hours=1),
            express_time=now - timedelta(minutes=45)
        ),

        Booking(
            code="BK_OLD",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(hours=1),
            express_time=now - timedelta(minutes=45)
        )
    ]
    test_session.add_all(bookings)
    test_session.commit()
    return bookings


@pytest.fixture
def sample_payments(test_session, sample_bookings):
    payments = [
        # Payment cho BK_PAID_1 (Đang chờ thanh toán)
        Payment(
            code="PAY_BK1",
            booking_code="BK_PAID_1",
            payment_method="momo",
            amount=50000,
            status=PaymentStatus.PENDING,
            type=PaymentType.PAYMENT,
            expired_time=datetime(2026, 4, 29, 21, 30, 0)
        ),

        # Payment cho BK_PAID_3 (Booking này bạn ghi chú là 'đã thanh toán xong xuôi')
        Payment(
            code="PAY_BK2",
            booking_code="BK_PAID_2",
            payment_method="momo",
            transaction_id="MOMO123456789",  # Giả lập đã có mã giao dịch
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT,
            expired_time = datetime(2026, 4, 29, 19, 30, 0)

    ),
        Payment(
            code="PAY_BK3",
            booking_code="BK_PAID_3",
            payment_method="momo",
            transaction_id="MOMO123456789",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT,
            expired_time=datetime(2026, 4, 16, 19, 30, 0)

        ),

        Payment(
            code="PAY_BK4",
            booking_code="BK_PAID_4",
            payment_method="momo",
            transaction_id="",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.REFUND,
            expired_time=datetime(2026, 4, 14, 19, 30, 0)

        ),

        # Payment cho BK_CRITICAL (Sắp hết hạn)
        Payment(
            code="PAY_CRITICAL",
            booking_code="BK_CRITICAL",
            payment_method="momo",
            amount=50000,
            status=PaymentStatus.PENDING,
            type=PaymentType.PAYMENT,
            expired_time=datetime(2026, 4, 14, 19, 15, 10)
        ),
        Payment(
            code="PAY_OLD",
            booking_code="BK_OLD",
            payment_method="momo",
            amount=50000,
            status=PaymentStatus.PENDING,
            type=PaymentType.PAYMENT,
            expired_time=datetime(2026, 4, 14, 19, 15, 10)
        )
    ]

    test_session.add_all(payments)
    test_session.commit()
    return payments

@pytest.fixture
def sample_tickets(test_session):
    # Dữ liệu Ticket tương ứng với các Booking trong sample_bookings
    tickets = [
        # Tickets cho BK_PAID_1 (Nhóm Valid - 2 vé cho đa dạng)
        Ticket(show_id=1, seat_code="A1", booking_code="BK_PAID_1", price=25000, active=True),
        Ticket(show_id=1, seat_code="A2", booking_code="BK_PAID_1", price=25000, active=True),

        # Ticket cho BK_PAID_2 (Nhóm Valid)
        Ticket(show_id=1, seat_code="B1", booking_code="BK_PAID_2", price=50000, active=True),

        # Ticket cho BK_PAID_3 (Nhóm Đã gọi callback)
        Ticket(show_id=1, seat_code="C1", booking_code="BK_PAID_3", price=50000, active=True),

        # Ticket cho BK_CRITICAL (Nhóm Sát nút hết hạn)
        Ticket(show_id=1, seat_code="D1", booking_code="BK_CRITICAL", price=50000, active=True),

        # Ticket cho BK_EXPIRED (Nhóm Đã hết hạn)
        Ticket(show_id=1, seat_code="E1", booking_code="BK_EXPIRED", price=50000, active=True),

        # Ticket cho BK_SUCCESS (Nhóm Đã thanh toán lâu rồi)
        Ticket(show_id=1, seat_code="F1", booking_code="BK_SUCCESS", price=50000, active=True)
    ]

    test_session.add_all(tickets)
    test_session.commit()
    return tickets


@pytest.fixture
def sample_shows(test_session):
    # Giả sử bạn đã có Film (id=1) và Room (id=1) trong DB rồi
    # Nếu chưa, bạn nên tạo Film/Room trước hoặc dùng ID có sẵn nếu là DB test cố định

    shows = [
        # Show ngày 2026-04-08 (Như trong ảnh)
        Show(id=1, start_time=datetime(2026, 4, 8, 14, 0, 0), film_id=1, room_id=1),
        Show(id=2, start_time=datetime(2026, 4, 8, 19, 30, 0), film_id=1, room_id=1),

        # Show ngày 2026-04-09
        Show(id=3, start_time=datetime(2026, 4, 9, 14, 0, 0), film_id=1, room_id=1),
        Show(id=4, start_time=datetime(2026, 4, 9, 19, 30, 0), film_id=1, room_id=1),

        # Show ngày 2026-04-10
        Show(id=5, start_time=datetime(2026, 4, 10, 14, 0, 0), film_id=1, room_id=1),
        Show(id=6, start_time=datetime(2026, 4, 10, 19, 30, 0), film_id=1, room_id=1),

        # Thêm các show khác cho film_id khác hoặc room_id khác nếu cần test logic lọc
        Show(id=9, start_time=datetime(2026, 4, 11, 20, 0, 0), film_id=2, room_id=2),
    ]

    test_session.add_all(shows)
    test_session.commit()
    return shows


@pytest.fixture
def sample_films(test_session):
    films = [
        # --- PHIM 1: Đang chiếu (Phù hợp với sample_shows ID 1-6) ---
        Film(
            id=1,
            title="Cuộc Chiến Đa Vũ Trụ",
            description="Một bộ phim hành động viễn tưởng đỉnh cao.",
            genre="Hành Động, Viễn Tưởng",
            age_limit=13,
            release_date=date(2026, 4, 1),
            expired_date=date(2026, 5, 1),
            poster="poster_multiverse.jpg",
            duration=120
        ),

        # --- PHIM 2: Đang chiếu (Phù hợp với sample_shows ID 9) ---
        Film(
            id=2,
            title="Hài Kịch Cuối Tuần",
            description="Những tình huống dở khóc dở cười.",
            genre="Hài Hước",
            age_limit=16,
            release_date=date(2026, 3, 15),
            expired_date=date(2026, 4, 25),
            poster="poster_comedy.jpg",
            duration=95
        ),

        # --- PHIM 3: Sắp chiếu (Chưa đến ngày release) ---
        Film(
            id=3,
            title="Thám Tử Lừng Danh 2026",
            description="Phim trinh thám kịch tính.",
            genre="Trinh Thám",
            age_limit=18,
            release_date=date(2026, 5, 1),
            expired_date=date(2026, 6, 1),
            poster="poster_detective.jpg",
            duration=110
        ),

        # --- PHIM 4: Đã hết hạn chiếu ---
        Film(
            id=4,
            title="Ký Ức Đã Qua",
            description="Phim tình cảm lãng mạn.",
            genre="Tình Cảm",
            age_limit=13,
            release_date=date(2026, 1, 1),
            expired_date=date(2026, 3, 30), # Đã hết hạn so với mốc 09/04/2026
            poster="poster_memory.jpg",
            duration=105
        )
    ]

    test_session.add_all(films)
    test_session.commit()
    return films


@pytest.fixture
def client(test_app):
    return test_app.test_client()

@pytest.fixture
def mock_jwt(mocker):
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=None)
    mocker.patch('flask_jwt_extended.utils.get_jwt_identity', return_value=4)
    mocker.patch('flask_jwt_extended.utils.get_jwt', return_value={'sub': 4})



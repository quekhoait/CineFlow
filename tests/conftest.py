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
            user_id=5,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=5),
            express_time=now + timedelta(minutes=10)  # Còn 10 phút
        ),
#Đ thành toán xong xuôi, gọi callback
        Booking(
            code="BK_PAID_3",
            user_id=5,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
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
        )
    ]
    test_session.add_all(bookings)
    test_session.commit()
    return bookings

@pytest.fixture
def client(test_app):
    return test_app.test_client()

@pytest.fixture
def mock_jwt(mocker):
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=None)

    # 2. Mock get_jwt_identity để trả về user_id = 4 (khớp với sample_bookings)
    # Lưu ý: Patch trực tiếp vào module utils của flask_jwt_extended
    mocker.patch('flask_jwt_extended.utils.get_jwt_identity', return_value=4)

    # 3. (Tùy chọn) Nếu code bạn gọi get_jwt(), hãy mock thêm nó
    mocker.patch('flask_jwt_extended.utils.get_jwt', return_value={'sub': 4})



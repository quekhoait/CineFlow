from datetime import timedelta, date
from app.api import api as api_blueprint
import pytest
from flask import Flask

from app import db
from app.models import Film

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["PAGE_SIZE"] = 2
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
def sample_films(test_session):
    today = date.today()

    films = [
        # --- NHÓM 1: PHIM ĐANG CHIẾU (Showing) ---
        # Điều kiện: release_date <= today <= expired_date
        Film(
            title="Lật Mặt 8: Kẻ Vô Diện",
            description="Phần mới nhất trong series ăn khách.",
            genre="Hành động",
            age_limit=16,
            release_date=today - timedelta(days=10),  # Chiếu được 10 ngày
            expired_date=today + timedelta(days=20),  # Còn 20 ngày nữa mới hết
            poster="lat_mat_8.jpg",
            duration=125
        ),
        Film(
            title="Mai 2",
            description="Câu chuyện tình cảm đầy nước mắt.",
            genre="Tâm lý",
            age_limit=18,
            release_date=today - timedelta(days=5),
            expired_date=today + timedelta(days=25),
            poster="mai_2.jpg",
            duration=140
        ),
        Film(
            title="Cuộc Chiến Đa Vũ Trụ",
            description="Siêu phẩm hành động viễn tưởng.",
            genre="Viễn tưởng",
            age_limit=13,
            release_date=today - timedelta(days=2),
            expired_date=today + timedelta(days=30),
            poster="multiverse.jpg",
            duration=150
        ),
        Film(
            title="Trạng Tí Phiêu Lưu Ký",
            description="Phim gia đình hấp dẫn.",
            genre="Gia đình",
            age_limit=0,
            release_date=today - timedelta(days=15),
            expired_date=today + timedelta(days=5),
            poster="trang_ti.jpg",
            duration=110
        ),

        # --- NHÓM 2: PHIM SẮP CHIẾU (Upcoming/Future) ---
        # Điều kiện: today < release_date
        Film(
            title="Conan Movie 2026",
            description="Thám tử lừng danh đối đầu tổ chức áo đen.",
            genre="Hoạt hình",
            age_limit=12,
            release_date=today + timedelta(days=7),  # 1 tuần nữa mới chiếu
            expired_date=today + timedelta(days=37),
            poster="conan_2026.jpg",
            duration=110
        ),
        Film(
            title="Avengers: Secret Wars",
            description="Trận chiến cuối cùng của MCU.",
            genre="Hành động",
            age_limit=13,
            release_date=today + timedelta(days=30),  # 1 tháng nữa
            expired_date=today + timedelta(days=60),
            poster="avengers_sw.jpg",
            duration=180
        ),
        Film(
            title="Sơn Tinh Thủy Tinh",
            description="Thần thoại Việt Nam kỹ xảo đỉnh cao.",
            genre="Thần thoại",
            age_limit=13,
            release_date=today + timedelta(days=15),
            expired_date=today + timedelta(days=45),
            poster="sttt.jpg",
            duration=120
        ),

        # --- NHÓM 3: PHIM ĐÃ HẾT HẠN (Expired/Past) ---
        # Điều kiện: expired_date < today
        Film(
            title="Bố Già",
            description="Phim đạt doanh thu kỷ lục.",
            genre="Gia đình",
            age_limit=13,
            release_date=today - timedelta(days=100),
            expired_date=today - timedelta(days=70),  # Đã hết hạn lâu rồi
            poster="bo_gia.jpg",
            duration=128
        ),
        Film(
            title="Doraemon: Nobita và Hòn Đảo Diệu Kỳ",
            description="Hành trình khám phá đảo hoang.",
            genre="Hoạt hình",
            age_limit=0,
            release_date=today - timedelta(days=60),
            expired_date=today - timedelta(days=30),
            poster="doraemon_old.jpg",
            duration=105
        ),
        Film(
            title="Godzilla vs Kong",
            description="Cuộc chiến giữa các đại quái thú.",
            genre="Hành động",
            age_limit=13,
            release_date=today - timedelta(days=45),
            expired_date=today - timedelta(days=1),  # Vừa hết hạn hôm qua
            poster="gvk.jpg",
            duration=115
        )
    ]

    test_session.add_all(films)
    test_session.commit()

    return films

@pytest.fixture
def client(test_app):
    return test_app.test_client()



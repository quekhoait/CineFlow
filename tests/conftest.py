from datetime import timedelta, date
from app.api import api as api_blueprint
import pytest
from flask import Flask

from app import db, Seat, SeatType, Room, Cinema, Show
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
        # Nhóm 1: Đang chiếu (ID 1-4)
        Film(id=1, title="Lật Mặt 8: Kẻ Vô Diện", genre="Hành động", release_date=today - timedelta(days=10), expired_date=today + timedelta(days=20), poster="lat_mat_8.jpg", duration=125),
        Film(id=2, title="Mai 2", genre="Tâm lý", release_date=today - timedelta(days=5), expired_date=today + timedelta(days=25), poster="mai_2.jpg", duration=140),
        Film(id=3, title="Cuộc Chiến Đa Vũ Trụ", genre="Viễn tưởng", release_date=today - timedelta(days=2), expired_date=today + timedelta(days=30), poster="multiverse.jpg", duration=150),
        Film(id=4, title="Trạng Tí Phiêu Lưu Ký", genre="Gia đình", release_date=today - timedelta(days=15), expired_date=today + timedelta(days=5), poster="trang_ti.jpg", duration=110),

        # Nhóm 2: Sắp chiếu (ID 5-7)
        Film(id=5, title="Conan Movie 2026", genre="Hoạt hình", release_date=today + timedelta(days=7), expired_date=today + timedelta(days=37), poster="conan_2026.jpg", duration=110),
        Film(id=6, title="Avengers: Secret Wars", genre="Hành động", release_date=today + timedelta(days=30), expired_date=today + timedelta(days=60), poster="avengers_sw.jpg", duration=180),
        Film(id=7, title="Sơn Tinh Thủy Tinh", genre="Thần thoại", release_date=today + timedelta(days=15), expired_date=today + timedelta(days=45), poster="sttt.jpg", duration=120),

        # Nhóm 3: Đã hết hạn (ID 8-10)
        Film(id=8, title="Bố Già", genre="Gia đình", release_date=today - timedelta(days=100), expired_date=today - timedelta(days=70), poster="bo_gia.jpg", duration=128),
        Film(id=9, title="Doraemon: Nobita và Hòn Đảo Diệu Kỳ", genre="Hoạt hình", release_date=today - timedelta(days=60), expired_date=today - timedelta(days=30), poster="doraemon_old.jpg", duration=105),
        Film(id=10, title="Godzilla vs Kong", genre="Hành động", release_date=today - timedelta(days=45), expired_date=today - timedelta(days=1), poster="gvk.jpg", duration=115)
    ]

    test_session.add_all(films)
    test_session.commit()
    return films


@pytest.fixture
def sample_cinema_system(test_session):
    # 1. Tạo Rạp (Cinema)
    cinemas = [
        Cinema(id=1, name="CGV Vincom", address="Quận 1, HCM", province="HCM", hotline="19001001"),
        Cinema(id=2, name="Lotte Cinema", address="Quận 7, HCM", province="HN", hotline="19002002"),
        Cinema(id=3, name="CGV Vincom 1", address="Quận 2, HCM", province="HCM", hotline="19001003"),
    ]
    test_session.add_all(cinemas)
    test_session.flush()

    # 2. Tạo Phòng (Room) - Kết nối với Cinema 1
    rooms = [
        Room(id=1, name="Phòng Chiếu IMAX", row="10", column=15, cinema_id=1),
        Room(id=2, name="Phòng Chiếu 02", row="8", column=12, cinema_id=2)
    ]
    test_session.add_all(rooms)
    test_session.flush()

    # 3. Tạo Ghế (Seat) - Tạo 5 ghế cho Phòng 1

    seats = []
    for i in range(1, 6):
        seats.append(Seat(
            code=f"P1-A{i:02d}",
            type=SeatType.SINGLE,
            row="A",
            column=i,
            room_id=1
        ))

    # Thêm 1 ghế đôi (Couple Seat)
    seats.append(Seat(
        code="P1-COUPLE-01",
        type=SeatType.COUPLE,
        row="K",
        column=1,
        room_id=2
    ))

    test_session.add_all(seats)
    test_session.commit()

    return {"cinema": cinemas, "room": rooms, "seats": seats}


@pytest.fixture
def sample_shows(test_session, sample_films, sample_cinema_system):
    from datetime import datetime, time, timedelta
    today = date.today()
    tomorrow = today + timedelta(days=1)

    shows = [
        # --- SUẤT CHIẾU HÔM NAY ---
        Show(
            id=1,
            start_time=datetime.combine(today, time(10, 0)),
            film_id=1, room_id=2
        ),
        Show(
            id=2,
            start_time=datetime.combine(today, time(20, 0)),
            film_id=2, room_id=1
        ),
        # --- SUẤT CHIẾU NGÀY MAI ---
        Show(id=3,
            start_time=datetime.combine(tomorrow, time(14, 0)),
            film_id=1, room_id=1
        ),
        Show(
            id=4,
            start_time=datetime.combine(tomorrow, time(18, 0)),
            film_id=2, room_id=2
        )
    ]

    test_session.add_all(shows)
    test_session.commit()
    return shows

@pytest.fixture
def client(test_app):
    return test_app.test_client()



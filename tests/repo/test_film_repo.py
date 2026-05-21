from datetime import date, timedelta, datetime
from unittest.mock import patch
from app.dto.film_dto import FilmResponse
from app.models import Cinema, Room, Seat, SeatType, Show, Rules, Ticket
from app.repository import film_repo, show_repo, cinema_repo
from app.services import film_service, cinema_service, show_service
from app.utils.errors import NotFoundError, IdError, InvalidDateError
import pytest
from app import db
from app.models.film import Film



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

@pytest.fixture(autouse=True)
def sample_films(app_context):
    today = date.today()

    films = [
        # --- PHIM 1: Đang chiếu (Bắt đầu từ 10 ngày trước, còn 20 ngày nữa mới hết) ---
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

        # --- PHIM 2: Đang chiếu (Sắp hết hạn - còn 2 ngày) ---
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

        # --- PHIM 3: Sắp chiếu (10 ngày nữa mới ra mắt) ---
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

        # --- PHIM 4: Đã hết hạn chiếu (Đã kết thúc từ 5 ngày trước) ---
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
        )
    ]
    db.session.add_all(films)
    db.session.commit()

@pytest.fixture(autouse=True)
def sample_cinema_system(app_context):
    # 1. Tạo Rạp (Cinema)
    cinemas = [
        Cinema(id=1, name="CGV Vincom", address="Quận 1, HCM", province="HCM", hotline="19001001"),
        Cinema(id=2, name="Lotte Cinema", address="Quận 7, HN", province="HN", hotline="19002002"),
        Cinema(id=3, name="CGV Vincom 1", address="Quận 2, HCM", province="HCM", hotline="19001003"),
    ]
    db.session.add_all(cinemas)
    db.session.flush()

    # 2. Tạo Phòng (Room) - Kết nối với Cinema 1
    rooms = [
        Room(id=1, name="Phòng Chiếu IMAX", row="10", column=15, cinema_id=1),
        Room(id=2, name="Phòng Chiếu 02", row="8", column=12, cinema_id=2)
    ]
    db.session.add_all(rooms)
    db.session.flush()

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

    db.session.add_all(seats)
    db.session.commit()

@pytest.fixture(autouse=True)
def sample_shows(app_context):
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
            start_time=datetime.combine(today, time(12, 0)),
            film_id=2, room_id=1
        ),
        Show(
            id=3,
            start_time=datetime.combine(today, time(14, 0)),
            film_id=2, room_id=1
        ),
        Show(
            id=4,
            start_time=datetime.combine(today, time(20, 0)),
            film_id=2, room_id=1
        ),
        Show(
            id=5,
            start_time=datetime.combine(today, time(16, 0)),
            film_id=2, room_id=1
        ),
        # --- SUẤT CHIẾU NGÀY MAI ---
        Show(id=6,
            start_time=datetime.combine(tomorrow, time(14, 0)),
            film_id=1, room_id=1
        ),
        Show(
            id=7,
            start_time=datetime.combine(tomorrow, time(18, 0)),
            film_id=2, room_id=2
        )
    ]
    db.session.add_all(shows)
    db.session.commit()

@pytest.fixture(autouse=True)
def sample_rules(app_context):
    rules = [
        Rules(
            id=1, name="SINGLE_WEEKDAY", type="VND", value=50000, active=True, user_id=1
        ),
        Rules(
            id=2, name="SINGLE_WEEKEND", type="VND", value=65000, active=True, user_id=1
        ),
        Rules(
            id=3, name="COUPLE_WEEKDAY", type="VND", value=100000, active=True, user_id=1
        ),
        Rules(
            id=4, name="COUPLE_WEEKEND", type="VND", value=125000, active=True, user_id=1
        )
    ]
    db.session.add_all(rules)
    db.session.commit()
    return rules

def test_repo_get_all_films():
    result = film_repo.get_all()
    assert len(result) == 3
    for film in result:
        assert film.expired_date > datetime.now().date()

def test_repo_get_film_by_id():
    res = film_repo.get_by_id(1)
    assert res.id == 1
    assert res.title == "Cuộc Chiến Đa Vũ Trụ"

def test_repo_get_by_id_not_found():
    result = film_repo.get_by_id(9999)
    assert result is None

def test_repo_get_by_title_ilike():
    result = film_repo.get_by_title("Cuộc Chiến")
    assert len(result) >= 1
    assert "Cuộc Chiến" in result[0].title


def test_repo_get_now_showing():
    result = film_repo.get_now_showing()
    now = date.today()
    for film in result:
        assert film.release_date <= now
        assert film.expired_date >= now

def test_repo_get_release_showing():
    result = film_repo.get_release_showing()
    now = date.today()
    for film in result:
        assert film.release_date > now


def test_repo_get_schedule_by_film_and_date():
    film_id = 1
    target_date = date.today()
    results = film_repo.get_schedule_by_film_and_date(film_id, target_date)
    assert len(results) == 1
    for cinema in results:
        assert hasattr(cinema, 'schedule')
        for show in cinema.schedule:
            assert show.film_id == film_id
            assert show.start_time.date() == target_date

            assert hasattr(show, 'room_name')
            assert show.room_name is not None

#show
def test_repo_get_show_by_show_id():
    result = show_repo.get_show_by_show_id(1)
    assert result.film_id == 1

def test_repo_get_show_by_show_not_found():
    result = show_repo.get_show_by_show_id(9999)
    assert result is None

def test_repo_get_booked_ticket():
    t1 = Ticket( show_id=1, seat_code="A1", booking_code="ABC1", price=100, active=True)
    t2 = Ticket( show_id=1, seat_code="A2", booking_code="ABC2", price=100, active=True)
    t3 = Ticket( show_id=1, seat_code="A3", booking_code="ABC3", price=100, active=False)
    db.session.add_all([t1, t2, t3])
    db.session.commit()
    booked_tickets = show_repo.get_booked_ticket(1)
    assert len(booked_tickets) == 2
    for t in booked_tickets:
        assert t.active is True

def test_repo_get_booked_ticket_not_found():
    result = show_repo.get_booked_ticket(9999)
    assert not result

def test_repo_get_rules():
    rule = Rules(
        name="SINGLE_WEEKDAY",
        type="VND",
        value=50000,
        active=True,
        user_id=1
    )
    db.session.add(rule)
    db.session.commit()
    result = show_repo.get_price_seats("SINGLE_WEEKDAY")
    assert result is not None
    assert result.name == "SINGLE_WEEKDAY"
    assert result.value == '50000'
    assert result.active is True

def test_repo_get_rules_not_found():
    rule = Rules(
        name="SINGLE_WEEKDAY",
        type="VND",
        value=50000,
        active=True,
        user_id=1
    )
    db.session.add(rule)
    db.session.commit()
    with pytest.raises(NotFoundError) as excinfo:
        show_repo.get_price_seats("SINGLE_WEEKDAY11")
    assert "No rule with name" in excinfo.value.message

#cinema
def test_get_all():
    cinemas = cinema_repo.get_all()
    assert len(cinemas) == 3
    assert cinemas[0].name == "CGV Vincom"


def test_get_films_schedule_by_cinemaId():
    film = cinema_repo.get_films_schedule_by_cinemaId(1, date.today())
    assert len(film) == 1

def test_get_films_schedule_by_cinemaId_not_found():
    films = cinema_repo.get_films_schedule_by_cinemaId(99, date.today())
    assert films == []

def test_get_by_id_not_found():
    result = cinema_repo.get_films_schedule_by_cinemaId(9999, date.today())
    assert result == []
    assert len(result) == 0

def test_get_films_schedule_no_show_on_date():
    future_date = (datetime.now() + timedelta(days=10)).date()
    films = cinema_repo.get_films_schedule_by_cinemaId(1, future_date)
    assert films == []

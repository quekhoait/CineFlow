from datetime import date, timedelta
from app.models import Cinema, Room, Seat, SeatType, Show, Rules
from app.utils.errors import NotFoundError
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



@pytest.mark.parametrize("strategy, expected_count", [
    (None, 3),
    ('all', 3),
    ("showing", 2),
    ("future", 1),
    ("111222", 3)
])
def test_get_films_by_strategy(client, strategy, expected_count):
    response = client.get(f'/api/films?strategy={strategy}')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data['data']) == expected_count

def test_get_film_by_id_success(client):
    response = client.get('/api/films/1')
    data = response.get_json()
    film = data['data']
    assert response.status_code == 200
    assert film['title'] == "Cuộc Chiến Đa Vũ Trụ"

def test_get_film_by_id_not_found(client, sample_films):
    response = client.get('/api/films/9999')
    data = response.get_json()
    assert response.status_code == 404
    assert data['status'] == "error"


@pytest.mark.parametrize("query_param, expected_status, expected_count, expected_title", [
    ("?title=Cuộc", 200, 1, "Cuộc Chiến Đa Vũ Trụ"),
    ("?title=Khoa", 404, 0, None),
    ("", 200, 3, None)
])
def test_search_films_logic(client, query_param, expected_status, expected_count, expected_title):
    response = client.get(f'/api/films/search{query_param}')
    data = response.get_json()
    assert response.status_code == expected_status
    assert len(data['data']) == expected_count
    if expected_title:
        assert data['data'][0]['title'] == expected_title

def test_get_schedule_by_film(client):
    response = client.get('/api/films/1/cinemas')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data['data']) == 1

def test_film_api_internal_error(mocker, client):
    mock_service  = mocker.patch('app.services.film_service.list')
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/films')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']
#

def test_list_film_api_internal_error(mocker, client):
    mock_service = mocker.patch('app.services.film_service.get_by_id')
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/films/1')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

def test_search_film_api_internal_error(mocker, client):
    mock_service = mocker.patch('app.services.film_service.get_by_title')
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/films/search?title=Lật')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

def test_get_cinemas_internal_error(mocker, client):
    mock_service = mocker.patch('app.services.film_service.get_schedule_by_film_and_date')
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/films/1/cinemas')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

def test_cinemas_api_not_found_error(mocker, client):
    mock_service = mocker.patch('app.services.film_service.get_schedule_by_film_and_date')
    mock_service.side_effect = NotFoundError("Cinema not found")
    response = client.get('/api/films/99/cinemas?date=2026-04-12')
    assert response.status_code == 404
    assert response.json['status'] == "error"
    assert response.json['message'] == "Cinema not found"
#
# #
# # ##############################################
def test_get_all_cinema(client):
    response = client.get('/api/cinemas')
    data = response.get_json()
    actual_data = data.get('data', [])
    c = sum(len(item['location']) for item in actual_data)
    assert response.status_code == 200
    assert c == 3

def test_list_cinema_api_internal_error(mocker, client):
    mock_service = mocker.patch('app.services.cinema_service.list')
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/cinemas')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

def test_get_cinema_by_id_success(client):
    response = client.get('/api/cinemas/1')
    data = response.get_json()
    assert response.status_code == 200
    assert data['data']['id'] == 1
    assert data['data']['name'] == 'CGV Vincom'
    assert data['status'] == "success"
#
def test_get_schedule_film_by_cinema_success(client):
    response = client.get('/api/cinemas/1/films')
    data = response.get_json()
    assert response.status_code == 200
    films = data['data']
    assert len(films) == 1
    first_film_schedule = films[0]['schedule']
    assert len(first_film_schedule) == 4

def test_get_cinema_by_id_error(client):
    response = client.get('/api/cinemas/99')
    assert response.status_code == 404

def test_get_cinema_by_date_error(client):
    response = client.get('/api/cinemas/1/films?date=2026-ab-12')
    assert response.status_code == 400

def test_get_film_api_internal_error(mocker, client):
    mock_service = mocker.patch('app.services.cinema_service.get_films_schedule_by_cinemaId')
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/cinemas/1/films')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']


def test_get_cinema_internal_error(mocker, client):
    mock_service = mocker.patch('app.services.cinema_service.get_by_id')
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/cinemas/1')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']


#
# # ###
# # # Show
@pytest.mark.parametrize("show_id, expected_status, count_seat", [
    (1, 200, 1),
    (999, 404, None),
    ("abc", 404, None)
])
def test_get_seats_by_show_api(client, mocker, show_id, expected_status, count_seat):
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=None)
    mocker.patch('flask_jwt_extended.get_jwt_identity', return_value=4)

    response = client.get(f'/api/shows/{show_id}')
    assert response.status_code == expected_status
    if expected_status == 200:
        data = response.get_json()
        assert len(data['data']['seats']) == count_seat
#
def test_get_seat_internal_error( mocker, client):
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=None)
    mocker.patch('flask_jwt_extended.get_jwt_identity', return_value=4)
    mock_service = mocker.patch('app.services.show_service.get_show_seats_info')
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/shows/1')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Have a problem while getting show seats info"
    assert "Database disconnected" in response.json['data']
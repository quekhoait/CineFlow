from datetime import date, timedelta
from app.models import Cinema, Room, Seat, SeatType, Show, Rules
from app.utils.errors import NotFoundError
import pytest
from app import db
from app.models.film import Film


@pytest.fixture(autouse=True)
def app_context():
    from app import create_app
    app = create_app('testing_fake')
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


#api
def test_film_workflow(client):
    list_res = client.get('/api/films?strategy=showing')
    assert list_res.status_code == 200
    list_data = list_res.get_json()
    assert list_data['status'] == "success"
    assert len(list_data) == 3


    search_title = "Hài Kịch Cuối Tuần"
    search_res = client.get(f'/api/films/search?title={search_title}')
    assert search_res.status_code == 200
    search_data = search_res.get_json()
    assert search_data['data'][0]['title'] == search_title

    film_id = search_data['data'][0]['id']
    detail_res = client.get(f'/api/films/{film_id}')
    assert detail_res.status_code == 200
    detail_data = detail_res.get_json()
    print(detail_data)
    assert detail_data['data']['title'] == "Hài Kịch Cuối Tuần"
    assert detail_data['message'] == "get film success"


    cinema_res = client.get(f'/api/films/{film_id}/cinemas?date=2024-05-20')
    assert cinema_res.status_code == 200
    assert cinema_res.get_json()['status'] == "success"
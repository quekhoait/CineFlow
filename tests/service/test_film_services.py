from datetime import date, timedelta, datetime, time
from unittest.mock import patch
from app.dto.film_dto import FilmResponse
from app.models import Cinema, Room, Seat, SeatType, Show, Rules
from app.services import film_service, cinema_service, show_service, rules_service
from app.utils.errors import NotFoundError, IdError, InvalidDateError
import pytest
from freezegun import freeze_time
from app import db
from app.models.film import Film
from freezegun import freeze_time


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
    today = date.today()
    fixed_date = date(2026, 4, 25)
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
        Show(
            id=6,
            start_time=datetime.combine(tomorrow, time(14, 0)),
            film_id=1, room_id=1
        ),
        Show(
            id=7,
            start_time=datetime.combine(tomorrow, time(18, 0)),
            film_id=2, room_id=2
        ),
        Show(
            id=8,
            start_time=datetime.combine(datetime(2026, 5, 3).date(), time(18, 0)),
            film_id=2, room_id=1
        ),
        Show(
            id=9,
            start_time=datetime.combine(datetime(2026, 4, 29).date(), time(18, 0)),
            film_id=2, room_id=1
        ),
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

@pytest.mark.parametrize("strategy", ["future", "showing", "all", None])
def test_service_list_strategies_logic(sample_films, strategy):
    result = film_service.list(strategy)
    today = date.today()
    assert isinstance(result, list)
    for film in result:
        res_date = datetime.strptime(film.get('release_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(film.get('expired_date'), '%Y-%m-%d').date()
        if strategy == "future":
            assert res_date > today
        elif strategy == "showing":
            assert res_date <= today and end_date >= today
        elif strategy == "all":
            assert len(result) == 3
        else:
            assert len(result) == 3


def test_service_list_exception_on_get_films(mocker):
    mock_get_films = mocker.patch('app.pattern.strategy_films.FilmFilterContext.get_films')
    mock_get_films.side_effect = Exception("Database connection failed")

    with pytest.raises(Exception) as excinfo:
        film_service.list("showing")
    assert "Database connection failed" in str(excinfo.value)

@pytest.mark.parametrize("title, expected_count, exception_class, expected_msg", [
    ("Cuộc", 1, None, None),
    ("Khoa", 0, NotFoundError, "Film not found"),
    (None, 3, None, None),
    ("", 3, None, None),
])
def test_service_get_by_title(title, expected_count, exception_class, expected_msg):
    if exception_class:
        with pytest.raises(exception_class) as excinfo:
            film_service.get_by_title(title)
        assert excinfo.value.message == expected_msg
    else:
        result = film_service.get_by_title(title)
        assert isinstance(result, list)
        assert len(result) == expected_count

        if title == "Cuộc":
            assert "Cuộc Chiến Đa Vũ Trụ" in result[0]['title']

@pytest.mark.parametrize("id, flag,  exception_class, expected_msg", [
    (1, True, None, None),
    (999, False, NotFoundError, "Film not found"),
    (-1, False, IdError, "ID must be a positive integer"),
    ("abc", False, IdError, "ID must be a number"),
    (None, False, IdError, "ID is required"),
])
def test_service_get_by_id(id, flag, exception_class, expected_msg):
    if flag :
        result = film_service.get_by_id(id)
        assert result.get('title') == "Cuộc Chiến Đa Vũ Trụ"
    else:
        with pytest.raises(exception_class) as excinfo:
            film_service.get_by_id(id)
        assert excinfo.value.message == expected_msg

@pytest.mark.parametrize("film_id, count_film, flag,  film_date, exception_class, expected_msg", [
    (1, 1, True, date.today(), None, None),
    (None, None, False, date.today(), IdError, "ID is required"),
    ("abc",  None,False, date.today(), IdError, "ID must be a number"),
    (0,  None,False, date.today(), IdError, "ID must be a positive integer"),
    (-1, None, False, date.today(), IdError, "ID must be a positive integer"),
    (99,  0,True, date.today(), None, []),
])
def test_get_schedule_validation_and_not_found(film_id, count_film, flag, film_date, sample_cinema_system, sample_shows, sample_films, exception_class, expected_msg):
    if flag:
        res = film_service.get_schedule_by_film_and_date(film_id, film_date)
        assert len(res) == count_film
    else:
        with pytest.raises(exception_class) as excinfo:
            film_service.get_schedule_by_film_and_date(film_id, film_date)
        assert excinfo.value.message == expected_msg

# #
# # ############
# # # cinema
def test_service_get_cinema(sample_cinema_system):
    res = cinema_service.list()
    assert isinstance(res, list)
    assert len(res) == 2

    hn_data = [item for item in res if item['province'] == 'HN']
    hcm_data = [item for item in res if item['province'] == 'HCM']
    assert isinstance(hcm_data, list)
    assert len(hcm_data[0]['location']) == 2
    assert isinstance(hn_data, list)
    assert len(hn_data[0]['location']) == 1
    assert hn_data[0]['location'][0]['name'] == "Lotte Cinema"
# #
# @pytest.mark.parametrize("cinema_id, date,title,  count_film, count_show", [
#     (1, None, "Hài Kịch Cuối Tuần", 1, 4),
#     (2, None, "Hài Kịch Cuối Tuần", 1, 0),
#     (1, date.today(), "Hài Kịch Cuối Tuần", 1, 4),
#     (999, None, [], 0, 0),
#     (1, "2005-10-30", [], 0, 0)
# ])
# def test_service_get_schedule_success(sample_cinema_system, sample_shows, sample_films, cinema_id, date, title ,count_film ,count_show):
#     res = cinema_service.get_films_schedule_by_cinemaId(cinema_id, date)
#     assert isinstance(res, list)
#     #Kiểm tra số lượng phim
#     assert len(res) == count_film
#     #Kiểm tra số lượng suất chiếu của 1 phim bất kỳ
#     result_show = [film for film in res if film['title'] == title]
#     if len(result_show) > 0:
#         assert len(result_show[0]['schedule']) == count_show
#     else:
#         assert len(result_show) == 0
#
@pytest.mark.parametrize("cinema_id, date,  exception_class, expected_msg", [
    (None, None, IdError, "ID is required"),
    (-1, None, IdError, "ID must be a positive integer"),
    ("abc", None, IdError, "ID must be a number"),
    (1, "abc", InvalidDateError,"Date invalid" ),
    (1, "ab-01-10", InvalidDateError, "Date invalid" ),
])
def test_service_get_schedule_error(cinema_id, date, exception_class, expected_msg):
    with pytest.raises(exception_class) as excinfo:
        cinema_service.get_films_schedule_by_cinemaId(cinema_id, date)
    assert excinfo.value.message == expected_msg



# @pytest.mark.parametrize("cinema_id, flag, exception_class, expected_msg", [
#     (1, True, None, None),
#     (999, False, NotFoundError, "cinema not found"),
#     (-1, False, IdError, "ID must be a positive integer"),
#     ("abc", False, IdError, "ID must be a number"),
#     (None, False, IdError, "ID is required"),
# ])
# def test_service_get_cinema_by_id(cinema_id, flag, exception_class, expected_msg):
#     if flag:
#         res = cinema_service.get_by_id(cinema_id)
#         assert res.get('id') == cinema_id
#     else:
#         with pytest.raises(exception_class) as excinfo:
#             cinema_service.get_by_id(cinema_id)
#         assert excinfo.value.message == expected_msg

def test_list_cinemas_exception(mocker):
    mock_repo = mocker.patch('app.repository.cinema_repo.get_all')
    mock_repo.side_effect = Exception("Database connection failed")
    with pytest.raises(Exception) as excinfo:
        cinema_service.list()
    assert "Database connection failed" in str(excinfo.value)
#
# # #####
# # # show

# @pytest.mark.parametrize("show_id, expected_count, price_name, mock_date", [
#     (8, 5, "SINGLE_WEEKEND", "2026-05-03"),  # Chủ Nhật (Cuối tuần)
#     (9, 5, "SINGLE_WEEKDAY", "2026-04-29"),  # Thứ Tư (Trong tuần)
# ])
# def test_service_get_show_seats_success(sample_rules, show_id, expected_count, price_name, mock_date):
#     with freeze_time(mock_date):
#         res = show_service.get_show_seats_info(show_id)
#         assert len(res['seats']) == expected_count
#         expected_price = next(
#             int(r.value) for r in sample_rules if r.name == price_name
#         )
#         for seat in res['seats']:
#             assert seat["price"] == expected_price
#             assert seat["is_booked"] is False
#         assert "film_title" in res
#         assert "cinema_name" in res

@pytest.mark.parametrize("show_id,  exception_class, expected_msg", [
    (None, IdError, "ID is required"),
    (-1, IdError, "ID must be a positive integer"),
    ("abc", IdError, "ID must be a number"),
    (999, NotFoundError, "Show not found"),
])
def test_service_get_show_seats_error(show_id, exception_class, expected_msg):
    with pytest.raises(exception_class) as excinfo:
        show_service.get_show_seats_info(show_id)
    assert excinfo.value.message == expected_msg


# def test_service_get_show_seats_missing_rule():
#     with pytest.raises(NotFoundError) as excinfo:
#         rules_service.rules()
#     assert "Rule not found" in str(excinfo.value.message)
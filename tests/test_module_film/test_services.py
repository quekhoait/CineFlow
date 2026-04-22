from datetime import datetime, date
from app.services import film_service, cinema_service, show_service
import pytest
from app.utils.errors import MissingTitleFilm, IdError, InvalidDateError, NotFoundError
from tests.conftest import sample_films, sample_cinema_system, sample_shows, sample_rules
import json
from unittest.mock import patch

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
            assert len(result) == 7
        else:
            assert len(result) == 7


@patch('app.pattern.strategy_films.FilmFilterContext.get_films')
def test_service_list_exception_on_get_films(mock_get_films):
    mock_get_films.side_effect = Exception("Database connection failed")

    with pytest.raises(Exception) as excinfo:
        film_service.list("showing")
    assert "Database connection failed" in str(excinfo.value)

@pytest.mark.parametrize("title, expected_count, exception_class, expected_msg", [
    ("Lật", 1, None, None),
    ("Khoa", 0, NotFoundError, "Film not found"),
    (None, 7, None, None),
    ("", 7, None, None),
])
def test_service_get_by_title(sample_films, title, expected_count, exception_class, expected_msg):
    if exception_class:
        with pytest.raises(exception_class) as excinfo:
            film_service.get_by_title(title)
        assert excinfo.value.message == expected_msg
    else:
        result = film_service.get_by_title(title)
        assert isinstance(result, list)
        assert len(result) == expected_count

        if title == "Lật":
            assert "Lật Mặt 8" in result[0]['title']

@pytest.mark.parametrize("id, flag,  exception_class, expected_msg", [
    (1, True, None, None),
    (999, False, NotFoundError, "Film not found"),
    (-1, False, IdError, "ID must be a positive integer"),
    ("abc", False, IdError, "ID must be a number"),
    (None, False, IdError, "ID is required"),
])
def test_service_get_by_id(sample_films, id, flag, exception_class, expected_msg):
    if flag :
        result = film_service.get_by_id(id)
        assert result.get('title') == "Lật Mặt 8: Kẻ Vô Diện"
    else:
        with pytest.raises(exception_class) as excinfo:
            film_service.get_by_id(id)
        assert excinfo.value.message == expected_msg


@pytest.mark.parametrize("film_id, flag,  film_date, exception_class, expected_msg", [
    (1, True, date.today(), None, None),
    (None, False, "2026-04-12", IdError, "ID is required"),
    ("abc", False, "2026-04-12", IdError, "ID must be a number"),
    (0, False, "2026-04-12", IdError, "ID must be a positive integer"),
    (-1, False, "2026-04-12", IdError, "ID must be a positive integer"),
    (99, False, "2026-04-12", NotFoundError, "Cinema not found"),
])
def test_get_schedule_validation_and_not_found(film_id, flag, film_date, sample_cinema_system, sample_shows, sample_films, exception_class, expected_msg):
    if flag:
        res = film_service.get_schedule_by_film_and_date(film_id, film_date)
        assert len(res) == 1
    else:
        with pytest.raises(exception_class) as excinfo:
            film_service.get_schedule_by_film_and_date(film_id, film_date)
        assert excinfo.value.message == expected_msg

#
# ############
# # cinema
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
#
@pytest.mark.parametrize("cinema_id, date,title,  count_film, count_show", [
    (1, None, "Mai 2", 2, 3), #rạp 1 phim mai 2
    (2,None, "Mai 2", 1, 0 ), #phim ko cos suaat chieu
    (1,date.today(), "Lật Mặt 8: Kẻ Vô Diện", 2, 1)
])
def test_service_get_schedule_success(sample_cinema_system, sample_shows, sample_films, cinema_id, date, title ,count_film ,count_show):
    res = cinema_service.get_films_schedule_by_cinemaId(cinema_id, date)
    assert isinstance(res, list)
    #Kiểm tra số lượng phim
    assert len(res) == count_film
    #Kiểm tra số lượng suất chiếu của 1 phim bất kỳ
    result_show = [film for film in res if film['title'] == title]
    if len(result_show) > 0:
        assert len(result_show[0]['schedule']) == count_show
    else:
        assert len(result_show) == 0

@pytest.mark.parametrize("cinema_id, date,  exception_class, expected_msg", [
    (None, None, IdError, "ID is required"),
    (-1, None, IdError, "ID must be a positive integer"),
    ("abc", None, IdError, "ID must be a number"),
    (999, None, NotFoundError, "Film not found"),
    (1, "abc", InvalidDateError,"Date invalid" ),
    (1, "ab-01-10", InvalidDateError, "Date invalid" ),
])
def test_service_get_schedule_error(sample_cinema_system, sample_shows, sample_films, cinema_id, date,
                              exception_class, expected_msg):
    with pytest.raises(exception_class) as excinfo:
        cinema_service.get_films_schedule_by_cinemaId(cinema_id, date)
    assert excinfo.value.message == expected_msg

@pytest.mark.parametrize("cinema_id, flag, exception_class, expected_msg", [
    (1, True, None, None),
    (999, False, NotFoundError, "cinema not found"),
    (-1, False, IdError, "ID must be a positive integer"),
    ("abc", False, IdError, "ID must be a number"),
    (None, False, IdError, "ID is required"),
])
def test_service_get_cinema_by_id(sample_cinema_system, sample_shows, sample_films, cinema_id, flag, exception_class, expected_msg):
    if flag:
        res = cinema_service.get_by_id(cinema_id)
        assert res.get('id') == cinema_id
    else:
        with pytest.raises(exception_class) as excinfo:
            cinema_service.get_by_id(cinema_id)
        assert excinfo.value.message == expected_msg

@patch('app.repository.cinema_repo.get_all')
def test_list_cinemas_exception(mock_repo):
    mock_repo.side_effect = Exception("Database connection failed")
    with pytest.raises(Exception) as excinfo:
        cinema_service.list()
    assert "Database connection failed" in str(excinfo.value)
#
# #####
# # show

@pytest.mark.parametrize("show_id, expected_count, price_name", [
    (1, 1, "COUPLE_WEEKDAY"), # Room 2 (1 ghế Couple), Thứ 6
    (2, 5, "SINGLE_WEEKDAY"), # Room 1 (5 ghế Single), Thứ 6
])
def test_service_get_show_seats_success(
    sample_cinema_system, sample_rules, sample_shows, sample_films,
    show_id, expected_count, price_name
):
    res = show_service.get_show_seats_info(show_id)
    assert len(res['seats']) == expected_count
    expected_price = next(
        int(r.value) for r in sample_rules if r.name == price_name
    )
    for seat in res['seats']:
        assert seat["price"] == expected_price
        assert seat["is_booked"] is False
    assert "film_title" in res
    assert "cinema_name" in res

@pytest.mark.parametrize("show_id,  exception_class, expected_msg", [
    (None, IdError, "ID is required"),
    (-1, IdError, "ID must be a positive integer"),
    ("abc", IdError, "ID must be a number"),
    (999, NotFoundError, "Show not found"),
])
def test_service_get_show_seats_error(sample_cinema_system, sample_rules, sample_shows, sample_films, show_id, exception_class, expected_msg):
    with pytest.raises(exception_class) as excinfo:
        show_service.get_show_seats_info(show_id)
    assert excinfo.value.message == expected_msg


def test_service_get_show_seats_missing_rule(sample_cinema_system, sample_shows, test_session):
    show_id = 1
    with pytest.raises(NotFoundError) as excinfo:
        show_service.get_show_seats_info(show_id)
    assert "No rule with name" in str(excinfo.value.message)




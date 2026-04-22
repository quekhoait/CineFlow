from datetime import datetime, date, timedelta
import pytest
from app import Ticket, Rules
from app.utils.errors import NotFoundError
from tests.conftest import sample_films, sample_shows, sample_cinema_system, test_session
from app.repository import film_repo, show_repo, cinema_repo


def test_repo_get_all_films(test_session, sample_films):
    result = film_repo.get_all()
    assert len(result) == 7
    for film in result:
        assert film.expired_date > datetime.now().date()

def test_repo_get_film_by_id(test_session, sample_films):
    res = film_repo.get_by_id(1)
    assert res.id == 1
    assert res.title == "Lật Mặt 8: Kẻ Vô Diện"

def test_repo_get_by_id_not_found(test_session):
    result = film_repo.get_by_id(9999)
    assert result is None

def test_repo_get_by_title_ilike(test_session, sample_films):
    result = film_repo.get_by_title("lật mặt")
    assert len(result) >= 1
    assert "Lật Mặt" in result[0].title


def test_repo_get_now_showing(test_session, sample_films):
    result = film_repo.get_now_showing()
    now = date.today()
    for film in result:
        assert film.release_date <= now
        assert film.expired_date >= now

def test_repo_get_release_showing(test_session, sample_films):
    result = film_repo.get_release_showing()
    now = date.today()
    for film in result:
        assert film.release_date > now


def test_repo_get_schedule_by_film_and_date(test_session, sample_cinema_system, sample_shows, sample_films):
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
def test_repo_get_show_by_show_id(test_session, sample_shows):
    result = show_repo.get_show_by_show_id(1)
    assert result.film_id == 1

def test_repo_get_show_by_show_not_found(test_session):
    result = show_repo.get_show_by_show_id(9999)
    assert result is None

def test_repo_get_booked_ticket(test_session):
    t1 = Ticket( show_id=1, seat_code="A1", booking_code="ABC1", price=100, active=True)
    t2 = Ticket( show_id=1, seat_code="A2", booking_code="ABC2", price=100, active=True)
    t3 = Ticket( show_id=1, seat_code="A3", booking_code="ABC3", price=100, active=False)
    test_session.add_all([t1, t2, t3])
    test_session.commit()
    booked_tickets = show_repo.get_booked_ticket(1)
    assert len(booked_tickets) == 2
    for t in booked_tickets:
        assert t.active is True

def test_repo_get_booked_ticket_not_found(sample_shows):
    result = show_repo.get_booked_ticket(9999)
    assert not result

def test_repo_get_rules(test_session):
    rule = Rules(
        name="SINGLE_WEEKDAY",
        type="VND",
        value=50000,
        active=True,
        user_id=1
    )
    test_session.add(rule)
    test_session.commit()
    result = show_repo.get_price_seats("SINGLE_WEEKDAY")
    assert result is not None
    assert result.name == "SINGLE_WEEKDAY"
    assert result.value == '50000'
    assert result.active is True

def test_repo_get_rules_not_found(test_session):
    rule = Rules(
        name="SINGLE_WEEKDAY",
        type="VND",
        value=50000,
        active=True,
        user_id=1
    )
    test_session.add(rule)
    test_session.commit()
    with pytest.raises(NotFoundError) as excinfo:
        show_repo.get_price_seats("SINGLE_WEEKDAY11")
    assert "No rule with name" in excinfo.value.message

#cinema
def test_get_all(sample_cinema_system):
    cinemas = cinema_repo.get_all()
    assert len(cinemas) == 3
    assert cinemas[0].name == "CGV Vincom"


def test_get_films_schedule_by_cinemaId(sample_cinema_system, sample_shows):
    film = cinema_repo.get_films_schedule_by_cinemaId(1, date.today())
    assert len(film) == 2

def test_get_films_schedule_by_cinemaId_not_found(sample_cinema_system, sample_shows):
    films = cinema_repo.get_films_schedule_by_cinemaId(99, date.today())
    assert films == []

def test_get_by_id_not_found(sample_cinema_system, sample_shows):
    result = cinema_repo.get_films_schedule_by_cinemaId(9999, date.today())
    assert result == []
    assert len(result) == 0

def test_get_films_schedule_no_show_on_date(sample_cinema_system, sample_shows):
    future_date = (datetime.now() + timedelta(days=10)).date()
    films = cinema_repo.get_films_schedule_by_cinemaId(1, future_date)
    assert films == []

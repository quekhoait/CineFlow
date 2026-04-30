import pytest
from datetime import date, datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.models.film import Film, Show


class TestFilmAndShowModels:
    @pytest.fixture
    def test_setup_film(self, test_session):
        film = Film(
            title="CineFlow Movie",
            poster="/static/movie.jpg",
            release_date=date.today(),
            duration=120
        )
        test_session.add(film)
        test_session.commit()
        return film

    def test_film_missing_required_fields(self, test_session):
        invalid_film = Film(description="Thiếu title và poster")
        test_session.add(invalid_film)

        with pytest.raises(IntegrityError):
            test_session.commit()
        test_session.rollback()

    def test_show_foreign_key_constraints(self, test_session, test_setup_film):
        film = test_setup_film
        invalid_show = Show(
            start_time=datetime.now(),
            film_id=film.id,
            room_id=999999
        )
        test_session.add(invalid_show)

        with pytest.raises(IntegrityError):
            test_session.commit()
        test_session.rollback()

    def test_successful_show_creation(self, test_session, test_setup_film, test_setup_cinema_and_room):
        film = test_setup_film
        room = test_setup_cinema_and_room

        valid_show = Show(
            start_time=datetime.now(),
            film_id=film.id,
            room_id=room.id
        )
        test_session.add(valid_show)
        test_session.commit()

        assert valid_show.id is not None
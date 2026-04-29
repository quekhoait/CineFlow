import pytest
import datetime
from unittest.mock import patch
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_refresh_token

from app import db, create_app
from app import models
from app.dto.booking_dto import BookingRequest
from app.services import booking_service
from app.utils.errors import NotFoundError, TicketExistError, UnauthorizedError


@pytest.fixture(autouse=True)
def app_context():
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture(autouse=True)
def setup_data():
    u1 = models.User(username='u1', password=generate_password_hash('Admin123@'),
                     full_name='u1', email='u1@gmail.com', role=models.RoleEnum.USER, is_active=True)
    db.session.add(u1)
    db.session.flush()

    cinema = models.Cinema(name="CineFlow Q9", address="Le Van Viet")
    db.session.add(cinema)
    db.session.flush()

    room = models.Room(name="Room 1", cinema_id=cinema.id)
    db.session.add(room)
    db.session.flush()

    seat1 = models.Seat(code="A1", type=models.SeatType.SINGLE, room_id=room.id)
    seat2 = models.Seat(code="A2", type=models.SeatType.SINGLE, room_id=room.id)
    seat3 = models.Seat(code="B1", type=models.SeatType.COUPLE, room_id=room.id)
    db.session.add_all([seat1, seat2, seat3])
    db.session.flush()

    film = models.Film(title="Test Film", poster="/poster.jpg", release_date=datetime.date.today())
    db.session.add(film)
    db.session.flush()

    show_time = datetime.datetime.now() + datetime.timedelta(days=1)
    show = models.Show(start_time=show_time, film_id=film.id, room_id=room.id)
    db.session.add(show)
    db.session.flush()

    rule1 = models.Rules(name="SINGLE_WEEKDAY", value="100000", user_id=u1.id)
    rule2 = models.Rules(name="SINGLE_WEEKEND", value="120000", user_id=u1.id)
    rule3 = models.Rules(name="COUPLE_WEEKDAY", value="200000", user_id=u1.id)
    rule4 = models.Rules(name="COUPLE_WEEKEND", value="240000", user_id=u1.id)
    db.session.add_all([rule1, rule2, rule3, rule4])

    db.session.commit()

    return {
        "user_id": u1.id,
        "show_id": show.id,
        "seat_codes": ["A1", "B1"]
    }


class TestBookingService:

    @patch('app.services.booking_service.get_jwt_identity')
    def test_add_booking_success(self, mock_jwt, setup_data):
        mock_jwt.return_value = setup_data["user_id"]
        request_data = BookingRequest()
        request_data.id_show = setup_data["show_id"]
        request_data.code_seats = ["A1", "B1"]
        response = booking_service.create(request_data)

        assert response is not None
        assert "code" in response
        assert response["code"].startswith("BK")

    @patch('app.services.booking_service.get_jwt_identity')
    def test_add_booking_show_not_found(self, mock_jwt, setup_data):
        mock_jwt.return_value = setup_data["user_id"]
        request_data = BookingRequest()
        request_data.id_show = 9999
        request_data.code_seats = ["A1"]
        with pytest.raises(NotFoundError):
            booking_service.create(request_data)

    @patch('app.services.booking_service.get_jwt_identity')
    def test_add_booking_seat_not_found(self, mock_jwt, setup_data):
        mock_jwt.return_value = setup_data["user_id"]
        request_data = BookingRequest()
        request_data.id_show = setup_data["show_id"]
        request_data.code_seats = ["A1", "Z99"]
        with pytest.raises(NotFoundError):
            booking_service.create(request_data)

    @patch('app.services.booking_service.get_jwt_identity')
    def test_add_booking_seat_already_booked(self, mock_jwt, setup_data):
        mock_jwt.return_value = setup_data["user_id"]
        request1 = BookingRequest()
        request1.id_show = setup_data["show_id"]
        request1.code_seats = ["A1"]
        booking_service.create(request1)

        request2 = BookingRequest()
        request2.id_show = setup_data["show_id"]
        request2.code_seats = ["A1"]

        with pytest.raises(TicketExistError):
            booking_service.create(request2)

    @patch('app.services.booking_service.get_jwt_identity')
    def test_add_booking_unauthorized(self, mock_jwt, setup_data):
        mock_jwt.return_value = None
        request_data = BookingRequest()
        request_data.id_show = setup_data["show_id"]
        request_data.code_seats = ["A1"]

        with pytest.raises(UnauthorizedError):
            booking_service.create(request_data)
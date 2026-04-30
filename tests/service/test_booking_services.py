import pytest
import datetime
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_refresh_token

from app import db, create_app
from app import models
from app.dto.booking_dto import BookingRequest
from app.models import BookingStatus
from app.services import booking_service
from app.utils.errors import NotFoundError, TicketExistError, UnauthorizedError, TicketCanceledError, \
    CancelCheckedInTicketError, ExpiredTicketError


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

    u2 = models.User(username='u2', password=generate_password_hash('Admin123@'),
                     full_name='u2', email='u2@gmail.com', role=models.RoleEnum.USER, is_active=True)
    db.session.add(u2)
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
    rule5 = models.Rules(name="CANCEL_HOUR", value="2", user_id=u1.id)
    db.session.add_all([rule1, rule2, rule3, rule4, rule5])

    db.session.commit()

    return {
        "user_id": u1.id,
        "show_id": show.id,
        "seat_codes": ["A1", "B1"]
    }

@patch('app.services.booking_service.get_jwt_identity')
def test_add_booking_success(mock_jwt, setup_data):
    mock_jwt.return_value = setup_data["user_id"]
    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"]
    request_data.code_seats = ["A1", "B1"]
    response = booking_service.create(request_data)

    assert response is not None
    assert "code" in response
    assert response["code"].startswith("BK")

@patch('app.services.booking_service.get_jwt_identity')
def test_add_booking_show_not_found(mock_jwt, setup_data):
    mock_jwt.return_value = setup_data["user_id"]
    request_data = BookingRequest()
    request_data.id_show = 9999
    request_data.code_seats = ["A1"]
    with pytest.raises(NotFoundError):
        booking_service.create(request_data)

@patch('app.services.booking_service.get_jwt_identity')
def test_add_booking_seat_not_found(mock_jwt, setup_data):
    mock_jwt.return_value = setup_data["user_id"]
    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"]
    request_data.code_seats = ["A1", "Z99"]
    with pytest.raises(NotFoundError):
        booking_service.create(request_data)

@patch('app.services.booking_service.get_jwt_identity')
def test_add_booking_seat_already_booked(mock_jwt, setup_data):
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
def test_add_booking_unauthorized(mock_jwt, setup_data):
    mock_jwt.return_value = None
    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"]
    request_data.code_seats = ["A1"]

    with pytest.raises(UnauthorizedError):
        booking_service.create(request_data)

@patch('app.services.booking_service.get_jwt_identity')
def test_get_bookings_success(mock_jwt, setup_data, app_context):
    mock_jwt.return_value = setup_data["user_id"]
    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"]
    request_data.code_seats = ["A1"]
    booking_service.create(request_data)

    with app_context.test_request_context('/?page=1&limit=5'):
        response = booking_service.get_bookings()

    assert response is not None
    assert "bookings" in response
    assert len(response["bookings"]) > 0

@patch('app.services.booking_service.get_jwt_identity')
def test_get_bookings_with_search_code(mock_jwt, setup_data, app_context):
    mock_jwt.return_value = setup_data["user_id"]
    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"]
    request_data.code_seats = ["B1"]
    create_resp = booking_service.create(request_data)
    booking_code = create_resp["code"]

    with app_context.test_request_context(f'/?q={booking_code}'):
        response = booking_service.get_bookings()

    assert response is not None
    assert len(response["bookings"]) > 0
    assert response["bookings"][0]["code"] == booking_code

@patch('app.services.booking_service.get_jwt_identity')
def test_get_booking_by_code_success(mock_jwt, setup_data):
    mock_jwt.return_value = setup_data["user_id"]
    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"]
    request_data.code_seats = ["A2"]
    create_resp = booking_service.create(request_data)
    booking_code = create_resp["code"]

    response = booking_service.get_booking_by_code(booking_code)

    assert response is not None
    assert response["code"] == booking_code
    assert "film_title" in response
    assert "start_time" in response

@patch('app.services.booking_service.get_jwt_identity')
def test_get_booking_by_code_not_found(mock_jwt, setup_data):
    mock_jwt.return_value = setup_data["user_id"]
    with pytest.raises(NotFoundError):
        booking_service.get_booking_by_code("BK999999")


@patch('app.services.booking_service.get_jwt_identity')
@patch('app.repository.booking_repo.create_booking')
def test_add_booking_db_exception(mock_create_booking, mock_jwt, setup_data):
    mock_jwt.return_value = setup_data["user_id"]
    mock_create_booking.side_effect = Exception("Fake DB Error")

    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"]
    request_data.code_seats = ["A1"]

    with pytest.raises(Exception) as excinfo:
        booking_service.create(request_data)

    assert "Fake DB Error" in str(excinfo.value)

@patch('app.services.booking_service.get_jwt_identity')
def test_get_bookings_with_search_film_title(mock_jwt, setup_data, app_context):
    mock_jwt.return_value = setup_data["user_id"]

    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"]
    request_data.code_seats = ["A1"]
    booking_service.create(request_data)

    with app_context.test_request_context('/?q=Test'):
        response = booking_service.get_bookings()

    assert response is not None
    assert len(response["bookings"]) > 0

@patch('app.services.booking_service.get_jwt_identity')
def test_get_bookings_no_search_query(mock_jwt, setup_data, app_context):
    mock_jwt.return_value = setup_data["user_id"]

    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"]
    request_data.code_seats = ["B1"]
    booking_service.create(request_data)

    with app_context.test_request_context('/'):
        response = booking_service.get_bookings()

    assert response is not None
    assert "bookings" in response

@patch('app.services.booking_service.get_jwt_identity')
def test_get_bookings_empty_list(mock_jwt, setup_data, app_context):
    mock_jwt.return_value = setup_data["user_id"]
    with app_context.test_request_context('/'):
        response = booking_service.get_bookings()

    assert response is not None
    assert "bookings" in response
    assert response["bookings"] == []


@pytest.mark.parametrize(
    'user_id, status, payment_status, has_check_in, space_time_start,trigger_db_error, expected_errors', [
        # Success
        (1, models.BookingStatus.BOOKED, models.BookingPaymentStatus.PENDING, False, 121, False, None),
        (1, models.BookingStatus.BOOKED, models.BookingPaymentStatus.PAID, False, 121, False, None),

        # Failed
        (1, models.BookingStatus.CANCELED, models.BookingPaymentStatus.PENDING, False, 121, False, TicketCanceledError),
        (1, models.BookingStatus.BOOKED, models.BookingPaymentStatus.PENDING, True, 121, False,
         CancelCheckedInTicketError),
        (1, models.BookingStatus.BOOKED, models.BookingPaymentStatus.PENDING, False, 120, False, ExpiredTicketError),
        (1, models.BookingStatus.BOOKED, models.BookingPaymentStatus.PENDING, False, 119, False, ExpiredTicketError),
        (1, models.BookingStatus.BOOKED, models.BookingPaymentStatus.PENDING, False, 0, False, ExpiredTicketError),
        (1, models.BookingStatus.BOOKED, models.BookingPaymentStatus.PENDING, False, -1, False, ExpiredTicketError),
        (1, models.BookingStatus.BOOKED, models.BookingPaymentStatus.PENDING, False, 121, True, Exception),
        (2, models.BookingStatus.BOOKED, models.BookingPaymentStatus.PENDING, False, 120, False, NotFoundError),
    ])
@patch('app.services.booking_service.url_for')
@patch('app.services.booking_service.threading.Thread')
@patch('app.services.booking_service.get_jwt_identity')
def test_cancel_booking(mock_jwt, mock_thread, mock_url_for, monkeypatch, user_id, status, payment_status, has_check_in,
                        space_time_start, trigger_db_error, expected_errors):
    mock_jwt.return_value = user_id
    mock_request = MagicMock()
    mock_request.cookies.to_dict.return_value = {'csrf_access_token': 'dummy_token'}
    monkeypatch.setattr('app.services.booking_service.request', mock_request)
    mock_url_for.return_value = "http://dummy/api/refund"
    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance
    mock_thread_instance.start.side_effect = Exception

    start_time = datetime.datetime.now() + datetime.timedelta(minutes=space_time_start)
    check_in_time = datetime.datetime.now() if has_check_in else None
    show = models.Show(film_id=1, start_time=start_time, room_id=1)
    booking = models.Booking(code="BK_CODE", total_price=100000, user_id=1, status=status, check_in=check_in_time,
                             payment_status=payment_status)
    db.session.add_all([show, booking])
    db.session.flush()
    ticket = models.Ticket(show_id=show.id, booking_code=booking.code, price=100000, seat_code="A1")
    db.session.add(ticket)
    db.session.commit()

    if trigger_db_error:
        with patch('app.services.booking_service.booking_repo.update_cancel_show_seats') as mock_update_seats:
            mock_update_seats.side_effect = Exception()

            with pytest.raises(Exception):
                booking_service.cancel(code=booking.code, method="momo")

            booking_re = models.Booking.query.filter_by(code=booking.code).first()
            assert booking_re.status.value != "CANCELED"
            ticket_re = booking_re.tickets
            assert all(t.active == True for t in ticket_re)
            mock_thread.assert_not_called()
    elif expected_errors:
        with pytest.raises(expected_errors):
            booking_service.cancel(code=booking.code, method="momo")
        mock_thread.assert_not_called()
    else:
        booking_service.cancel(code=booking.code, method="momo")
        booking_re = models.Booking.query.filter_by(code=booking.code).first()
        assert booking_re.status.value == "CANCELED"
        ticket_re = booking_re.tickets
        assert all(t.active == False for t in ticket_re)
        if booking.payment_status == models.BookingPaymentStatus.PAID:
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
        else:
            mock_thread.assert_not_called()
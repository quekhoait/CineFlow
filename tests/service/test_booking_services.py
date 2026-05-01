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
from app.repository import booking_repo
from app.utils.errors import (NotFoundError, TicketExistError, UnauthorizedError, TicketCanceledError,
                              CancelCheckedInTicketError, ExpiredTicketError, ExpiredError, LimitBookingError)


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
    u2 = models.User(username='u2', password=generate_password_hash('Admin123@'),
                     full_name='u2', email='u2@gmail.com', role=models.RoleEnum.USER, is_active=True)
    db.session.add_all([u1, u2])
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

@pytest.mark.parametrize(
    'is_auth, show_val, code_seats, pre_book, is_expired, trigger_db_error, expected_errors', [
        (True, 'valid', ["A1", "B1"], False, False, False, None),
        # fail cases
        (False, 'valid', ["A1"], False, False, False, UnauthorizedError),
        (True, 9999, ["A1"], False, False, False, NotFoundError),
        (True, 'valid', ["A1", "Z99"], False, False, False, NotFoundError),
        (True, 'valid', ["A1"], True, False, False, TicketExistError),
        (True, 'valid', ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9"], False, False, False, LimitBookingError),
        (True, 'valid', ["A1"], False, True, False, ExpiredError),
        (True, 'valid', ["A1"], False, False, True, Exception),
    ]
)

@patch('app.services.booking_service.get_jwt_identity')
def test_create_booking(mock_jwt, setup_data, is_auth, show_val, code_seats, pre_book, is_expired, trigger_db_error,
                        expected_errors):
    mock_jwt.return_value = setup_data["user_id"] if is_auth else None
    if is_expired:
        show = db.session.get(models.Show, setup_data["show_id"])
        show.start_time = datetime.datetime.now() - datetime.timedelta(days=1)
        db.session.commit()

    if pre_book:
        req_pre = BookingRequest()
        req_pre.id_show = setup_data["show_id"]
        req_pre.code_seats = code_seats
        booking_service.create(req_pre)

    request_data = BookingRequest()
    request_data.id_show = setup_data["show_id"] if show_val == 'valid' else show_val
    request_data.code_seats = code_seats

    if trigger_db_error:
        with patch('app.repository.booking_repo.create_booking') as mock_db:
            mock_db.side_effect = Exception("DB Error")
            with pytest.raises(Exception):
                booking_service.create(request_data)
    elif expected_errors:
        with pytest.raises(expected_errors):
            booking_service.create(request_data)
    else:
        response = booking_service.create(request_data)
        assert response is not None
        assert response["code"].startswith("BK")

@pytest.mark.parametrize(
    'has_data, search_type', [
        (True, 'default'),
        (True, 'pagination'),
        (True, 'film'),
        (True, 'code'),
        (False, 'default'),
    ]
)

@patch('app.services.booking_service.get_jwt_identity')
def test_get_bookings(mock_jwt, setup_data, app_context, has_data, search_type):
    mock_jwt.return_value = setup_data["user_id"]
    url_path = '/'
    booking_code = None

    if has_data:
        req = BookingRequest()
        req.id_show = setup_data["show_id"]
        req.code_seats = ["A1"]
        resp = booking_service.create(req)
        booking_code = resp["code"]

        if search_type == 'pagination':
            url_path = '/?page=1&limit=5'
        elif search_type == 'film':
            url_path = '/?q=Test'
        elif search_type == 'code':
            url_path = f'/?q={booking_code}'

    with app_context.test_request_context(url_path):
        response = booking_service.get_bookings()

    assert response is not None
    assert "bookings" in response
    if has_data:
        assert len(response["bookings"]) > 0
        if search_type == 'code':
            assert response["bookings"][0]["code"] == booking_code
    else:
        assert response["bookings"] == []

@pytest.mark.parametrize('is_valid_code, expected_errors', [
    (True, None),
    (False, NotFoundError)
])

@patch('app.services.booking_service.get_jwt_identity')
def test_get_booking_by_code(mock_jwt, setup_data, is_valid_code, expected_errors):
    mock_jwt.return_value = setup_data["user_id"]
    req = BookingRequest()
    req.id_show = setup_data["show_id"]
    req.code_seats = ["A2"]
    resp = booking_service.create(req)
    real_code = resp["code"]
    test_code = real_code if is_valid_code else "BK999999"

    if expected_errors:
        with pytest.raises(expected_errors):
            booking_service.get_booking_by_code(test_code)
    else:
        response = booking_service.get_booking_by_code(test_code)
        assert response["code"] == real_code
        assert "film_title" in response

@pytest.mark.parametrize('is_valid_code, expected_errors', [
    (True, None),
    (False, NotFoundError)
])
def test_get_seat_by_code(setup_data, app_context, is_valid_code, expected_errors):
    with patch('app.services.booking_service.get_jwt_identity', return_value=setup_data["user_id"]):
        req = BookingRequest()
        req.id_show = setup_data["show_id"]
        req.code_seats = ["B1"]
        resp = booking_service.create(req)
        real_code = resp["code"]

    test_code = real_code if is_valid_code else "FAKE_CODE"

    if expected_errors:
        with pytest.raises(expected_errors):
            booking_service.get_seat_by_code(test_code)
    else:
        response = booking_service.get_seat_by_code(test_code)
        assert isinstance(response, list)
        assert len(response) > 0


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

def test_repo_update_booking_status_not_found(app_context):
    from app.repository import booking_repo
    with pytest.raises(NotFoundError):
        booking_repo.update_booking_status(user_id=9999, booking_code="FAKE_CODE", status="BOOKED")

def test_repo_update_cancel_show_seats_not_found(app_context):
    from app.repository import booking_repo
    with pytest.raises(NotFoundError):
        booking_repo.update_cancel_show_seats(user_id=9999, booking_code="FAKE_CODE")

def test_repo_get_rules_by_names_not_found(app_context):
    from app.repository import booking_repo
    with pytest.raises(NotFoundError):
        booking_repo.get_rules_by_names(["SINGLE_WEEKDAY", "RULE_FAKE"])
from unittest.mock import patch
import pytest
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import ValidationError
from app import create_app, db
from app.utils.errors import NotFoundError, APIError, ExpiredError, TicketCanceledError, CancelCheckedInTicketError, \
    ExpiredTicketError


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
def client(app_context):
    return app_context.test_client()


def assert_response(response, status_code):
    assert response.status_code == status_code
    json_data = response.get_json()
    assert 'message' in json_data
    assert 'status' in json_data
    return json_data


@pytest.mark.parametrize("is_authenticated, errors, status_code", [
    (True, None, 200),
    (True, Exception, 500),
    (False, None, 401),
])
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('app.api.booking_api.booking_service.get_bookings')
def test_get_bookings(mock_get_bookings, mock_jwt, client, is_authenticated, errors, status_code):
    if is_authenticated:
        mock_jwt.return_value = None
    else:
        mock_jwt.side_effect = NoAuthorizationError()

    if errors:
        mock_get_bookings.side_effect = errors
    else:
        mock_get_bookings.return_value = []

    response = client.get('/api/bookings')
    assert_response(response, status_code)
    if status_code == 200:
        assert 'success' == response.json['status']
        mock_get_bookings.assert_called_once()
    else:
        assert 'error' == response.json['status']


@pytest.mark.parametrize("is_authenticated, id_show, code_seats, errors, status_code", [
    (True, 1, ["A1"], None, 201),
    (True, None, ["A1"], ValidationError, 400),
    (True, 1, None, ValidationError, 400),
    (True, 1, [], ValidationError, 400),
    (True, 1, ["A1"], Exception, 500),
    (True, 1, ["A1"], NotFoundError, 404),
    (True, 1, ["A1"], ExpiredError, 400),
    (False, 1, ["A1"], None, 401),
])
@patch('app.api.booking_api.booking_service')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_create_booking(mock_jwt, mock_service, client, is_authenticated, id_show, code_seats, errors, status_code):
    if is_authenticated:
        mock_jwt.return_value = None
    else:
        mock_jwt.side_effect = NoAuthorizationError()

    payload = {
        'id_show': id_show,
        'code_seats': code_seats,
    }

    response = {"code": "BK_NORMAL"}

    if errors:
        mock_service.create.side_effect = errors
    else:
        mock_service.create.return_value = response

    response = client.post('/api/bookings/create', json=payload)
    json_data = assert_response(response, status_code)

    if status_code == 201:
        assert 'success' == json_data['status']
        assert 'code' in json_data['data']
        assert 'BK_NORMAL' in json_data['data']['code']

    elif errors in [ValidationError] or status_code == 401:
        mock_service.create.assert_not_called()
    else:
        mock_service.create.assert_called_once()


@pytest.mark.parametrize("errors, is_authenticated, status_code", [
    (None, True, 200),
    (NotFoundError, True, 404),
    (Exception, True, 500),
    (None, False, 401),
])
@patch('app.api.booking_api.booking_service.get_booking_by_code')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_get_booking(mock_jwt, mock_get, client, is_authenticated, errors, status_code):
    if is_authenticated:
        mock_jwt.return_value = None
    else:
        mock_jwt.side_effect = NoAuthorizationError()

    response = {
        "code": "BK_NORMAL",
        "film_title": "Film Title",
        "poster": "http://poster",
        "cinema": "Cinema",
        "total_price": "Total Price",
    }
    if errors:
        mock_get.side_effect = errors()
    else:
        mock_get.return_value = response

    response = client.get('/api/bookings/BK_NORMAL')

    json_data = assert_response(response, status_code)

    if status_code == 200:
        assert 'data' in json_data
        assert 'success' in json_data['status']
        mock_get.assert_called_once()
    else:
        assert 'error' == json_data['status']
        if not is_authenticated:
            mock_get.assert_not_called()


@pytest.mark.parametrize("is_authenticated, method, errors, status_code", [
    (True, "momo", None, 200),
    (True, "momo", Exception, 500),
    (True, "momo", TicketCanceledError, 400),
    (True, "momo", CancelCheckedInTicketError, 400),
    (True, "momo", ExpiredTicketError, 400),
    (True, "", ValidationError, 400),
    (True, None, ValidationError, 400),
    (False, "momo", None, 401),
])
@patch('app.api.booking_api.booking_service.cancel')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_cancel_booking(mock_jwt, mock_cancel, client, is_authenticated, method, errors, status_code):
    if is_authenticated:
        mock_jwt.return_value = None
    else:
        mock_jwt.side_effect = NoAuthorizationError()

    payload = {"method": method if method else {}}

    if errors is not ValidationError:
        mock_cancel.side_effect = errors
    else:
        mock_cancel.return_value = None

    response = client.post('/api/bookings/ABC123/cancel', json=payload)
    json_data = assert_response(response, status_code)

    if status_code == 200:
        assert 'success' == json_data['status']
        mock_cancel.assert_called_once()
    elif errors:
        assert 'error' == json_data['status']
        if errors == ValidationError:
            assert 'data' in json_data
        else:
            mock_cancel.assert_called_once()

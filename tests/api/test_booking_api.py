from unittest.mock import patch
import pytest
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import ValidationError
from app import create_app, db
from app.utils.errors import NotFoundError, APIError

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
        mock_get_bookings.assert_called_once()

@pytest.mark.parametrize("payload, errors, status_code", [
    ({"valid": "data"}, None, 201),
    ({"invalid": "data"}, ValidationError, 400),
    ({"valid": "data"}, Exception, 500),
])
@patch('app.api.booking_api.booking_service.create')
@patch('app.dto.booking_dto.BookingRequest.load')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_create_booking(mock_jwt, mock_load, mock_create, client, payload, errors, status_code):
    mock_jwt.return_value = None

    if errors is ValidationError:
        mock_load.side_effect = ValidationError({"field": ["invalid"]})
    else:
        mock_load.return_value = payload

    if errors and errors is not ValidationError:
        mock_create.side_effect = errors
    else:
        mock_create.return_value = {"id": 1}

    response = client.post('/api/bookings/create', json=payload)

    json_data = assert_response(response, status_code)

    if status_code == 201:
        assert json_data['status'] == 'success'
        mock_create.assert_called_once()
    elif errors is ValidationError:
        mock_create.assert_not_called()

@pytest.mark.parametrize("errors, status_code", [
    (None, 200),
    (NotFoundError, 404),
    (Exception, 500),
])
@patch('app.api.booking_api.booking_service.get_booking_by_code')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_get_booking(mock_jwt, mock_get, client, errors, status_code):
    mock_jwt.return_value = None

    if isinstance(errors, NotFoundError):
        mock_get.side_effect = errors
    elif errors:
        mock_get.side_effect = errors
    else:
        mock_get.return_value = {"code": "ABC123"}

    response = client.get('/api/bookings/ABC123')

    json_data = assert_response(response, status_code)

    if status_code == 200:
        assert 'data' in json_data
        assert 'code' in json_data['data']
        mock_get.assert_called_once()

@pytest.mark.parametrize("payload, errors, status_code", [
    ({"method": "bank"}, None, 200),
    ({"method": "bank"}, APIError(message="Fail", status_code=400), 400),
    ({"method": "bank"}, Exception, 500),
])
@patch('app.api.booking_api.booking_service.cancel')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_cancel_booking(mock_jwt, mock_cancel, client, payload, errors, status_code):
    mock_jwt.return_value = None

    if isinstance(errors, APIError):
        mock_cancel.side_effect = errors
    elif errors:
        mock_cancel.side_effect = errors

    response = client.post('/api/bookings/ABC123/cancel', json=payload)

    assert_response(response, status_code)

    if status_code == 200:
        mock_cancel.assert_called_once_with("ABC123", payload['method'])
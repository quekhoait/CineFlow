import io
from unittest.mock import patch
import pytest
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import ValidationError

from app import create_app, db
from app.utils.errors import ExistingUserError, SendNotificationFailed, InvalidOtpError, UserLoginEmailFailed, \
    UserLoginGoogleFailed, UnauthorizedError


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


@pytest.mark.parametrize('email,errors,status', [
    ("test@gmail.com", None, 200),
    ("test", ValidationError, 400),
    ("", ValidationError, 400),
    ("test@gmail.com", ExistingUserError, 409),
    ("test@gmail.com", SendNotificationFailed, 500),
    ("test@gmail.com", Exception, 500),
])
@patch('app.api.user_api.user_service.send_otp')
def test_send_otp(mock_send_otp, email, errors, status, client):
    if errors: mock_send_otp.side_effect = errors
    response = client.post(f'/api/user/send-otp', json={"email": email})

    assert response.status_code == status
    if errors is ValidationError:
        mock_send_otp.assert_not_called()
    else:
        mock_send_otp.assert_called_once()


@pytest.mark.parametrize('full_name, email, username, password, otp, errors, status', [
    # Success
    ("Nguyen Van A", "test@gmail.com", "usertest", "Password123!", "123456", None, 201),
    ("Nguyen Van A", "test@gmail.com ", "usertest", "Password123!", "123456", None, 201),
    ("Nguyen Van A", " test@gmail.com ", " usertest ", "Password123!", "123456", None, 201),
    # Error register
    ("Nguyen Van A", "exist@gmail.com", "usertest", "Password123!", "123456", ExistingUserError, 409),
    ("Nguyen Van A", "test@gmail.com", "usertest", "Password123!", "000000", InvalidOtpError, 400),
    ("Nguyen Van A", "test@gmail.com", "usertest", "Password123!", "123456", Exception, 500),
    # Invalid input
    ("", "test@gmail.com", "usertest", "Password123!", "123456", ValidationError, 400),
    ("     ", "test@gmail.com", "usertest", "Password123!", "123456", ValidationError, 400),
    ("Nguyen Van A", "", "usertest", "Password123!", "123456", ValidationError, 400),
    ("Nguyen Van A", "     ", "usertest", "Password123!", "123456", ValidationError, 400),
    ("Nguyen Van A", "wrong-email", "usertest", "Password123!", "123456", ValidationError, 400),
    ("Nguyen Van A", "test@gmail.com", "", "Password123!", "123456", ValidationError, 400),
    ("Nguyen Van A", "test@gmail.com", "usertest", "", "123456", ValidationError, 400),
    ("Nguyen Van A", "test@gmail.com", "usertest", "Password123", "123456", ValidationError, 400),
    ("Nguyen Van A", "test@gmail.com", "usertest", "password123!", "123456", ValidationError, 400),
    ("Nguyen Van A", "test@gmail.com", "usertest", "Password!", "123456", ValidationError, 400),
    ("Nguyen Van A", "test@gmail.com", "usertest", "Password!", 123548, ValidationError, 400),
    ("Nguyen Van A", "test@gmail.com", "usertest", "Password123!", "", ValidationError, 400),
])
@patch('app.api.user_api.user_service.register')
def test_register(mock_register, full_name, email, username, password, otp, errors, status, client):
    if errors is not ValidationError:
        mock_register.side_effect = errors

    payload = {
        "full_name": full_name,
        "email": email,
        "username": username,
        "password": password,
        "otp": otp
    }

    response = client.post('/api/user/register', json=payload)

    assert response.status_code == status
    assert 'message' in response.json
    assert 'status' in response.json

    if errors is ValidationError:
        mock_register.assert_not_called()
    else:
        mock_register.assert_called_once()


@pytest.mark.parametrize('provider, email, password, errors, status_code', [
    # Success
    ("email", "test@gmail.com", 'Abc123@', None, 200),
    ("google", None, None, None, 200),

    # Invalid input
    ("email", "", 'Abc123@', ValidationError, 400),
    ("email", "    ", 'Abc123@', ValidationError, 400),
    ("email", "test@gmail.com", '', ValidationError, 400),
    ("email", "wrong_email", 'Abc123@', ValidationError, 400),
    ("email", "test@gmail.com", 'Abc123', ValidationError, 400),
    ("email", "test@gmail.com", 'Abc@', ValidationError, 400),
    ("email", "test@gmail.com", 'bc123@', ValidationError, 400),

    # Error register
    ("email", "test@gmail.com", 'Abc123@', UserLoginEmailFailed, 400),
    ("email", "test@gmail.com", 'Abc123@', Exception, 500),
    ("google", None, None, Exception, 500),

])
@patch('app.api.user_api.user_service.authenticate')
def test_authenticate_email_api(mock_authenticate, client, provider, email, password, errors, status_code):
    if provider == "email":
        payload = {
            "email": email,
            "password": password,
        }

        if errors is None:
            mock_authenticate.return_value = {
                'access_token': "access_token",
                'refresh_token': "refresh_token",
            }
        elif errors is not ValidationError:
            mock_authenticate.side_effect = errors

        response = client.post('/api/user/auth/email', json=payload)
        response_json = response.get_json()

        assert response.status_code == status_code
        assert 'message' in response_json
        assert 'status' in response_json

        if errors is ValidationError:
            mock_authenticate.assert_not_called()
            cookies = response.headers.getlist('Set-Cookie')
            assert len(cookies) == 0

        else:
            mock_authenticate.assert_called_once()
            if errors is None:
                cookies = response.headers.getlist('Set-Cookie')
                assert len(cookies) >= 2
                assert any("access_token_cookie=access_token" in c and "HttpOnly" in c for c in cookies)
                assert any("refresh_token_cookie=refresh_token" in c and "HttpOnly" in c for c in cookies)
    else:
        if errors is None:
            mock_authenticate.return_value = {
                'url': 'http://127.0.0.1:8000/',
            }

        if errors is not ValidationError:
            mock_authenticate.side_effect = errors

        response = client.get(f'/api/user/auth/{provider}')
        response_json = response.get_json()
        assert response.status_code == status_code
        assert 'message' in response_json
        assert 'status' in response_json

        if errors is ValidationError:
            mock_authenticate.assert_not_called()
        else:
            mock_authenticate.assert_called_once()
            if errors is None:
                assert 'data' in response_json
                assert 'url' in response_json['data']


@pytest.mark.parametrize('provider, errors, status', [
    # Success
    ("google", None, 302),

    # Error from service
    ("google", UserLoginGoogleFailed, 400),
    ("google", Exception, 500),
])
@patch('app.api.user_api.user_service.callback')
def test_callback_api(mock_callback, client, provider, errors, status):
    if errors is None:
        mock_callback.return_value = {
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "redirect": "http://127.0.0.1:8000/",
        }
    elif errors is not ValidationError:
        mock_callback.side_effect = errors

    response = client.get(f'/api/user/auth/{provider}/callback')

    assert response.status_code == status
    if errors is None:
        assert response.location == "http://127.0.0.1:8000/"
        cookies = response.headers.getlist('Set-Cookie')
        assert len(cookies) >= 2
        assert any("access_token_cookie=access_token" in c and "HttpOnly" in c for c in cookies)
        assert any("refresh_token_cookie=refresh_token" in c and "HttpOnly" in c for c in cookies)

    else:
        response_json = response.get_json()

        assert 'message' in response_json
        assert 'status' in response_json
        if errors is ValidationError:
            mock_callback.assert_not_called()
        else:
            mock_callback.assert_called_once()


@pytest.mark.parametrize('is_authenticated,errors, status_code', [
    (True, None, 200),
    (True, UnauthorizedError, 401),
    (True, Exception, 500),
    (False, NoAuthorizationError, 401),
])
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('app.api.user_api.user_service.refresh')
def test_refresh_api(mock_refresh, mock_jwt, client, is_authenticated, errors, status_code):
    if is_authenticated:
        mock_jwt.return_value = None
    else:
        mock_jwt.side_effect = NoAuthorizationError()

    if errors is None:
        mock_refresh.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        }
    elif errors is not ValidationError:
        mock_refresh.side_effect = errors

    response = client.post('/api/user/auth/refresh')

    assert response.status_code == status_code

    if status_code == 200:
        mock_refresh.assert_called_once()
        cookies = response.headers.getlist('Set-Cookie')
        assert len(cookies) >= 2
        assert any("access_token_cookie=new_access_token" in c and "HttpOnly" in c for c in cookies)
        assert any("refresh_token_cookie=new_refresh_token" in c and "HttpOnly" in c for c in cookies)


@pytest.mark.parametrize('is_authenticated, status_code', [
    (True, 200),
    (False, 401),
])
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_auth_me_api(mock_verify_jwt, client, is_authenticated, status_code):
    if is_authenticated:
        mock_verify_jwt.return_value = None
    else:
        mock_verify_jwt.side_effect = NoAuthorizationError()

    response = client.get('/api/user/auth/me')
    assert response.status_code == status_code
    if is_authenticated:
        assert 'status' in response.json
        assert 'success' == response.json['status']


@pytest.mark.parametrize('is_authenticated, errors, status_code', [
    # Success
    (True, None, 200),
    # Error
    (False, None, 401),
    (True, Exception, 500),
])
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('app.api.user_api.user_service.profile')
def test_get_profile(mock_profile, mock_jwt, is_authenticated, errors, status_code, client):
    if is_authenticated:
        mock_jwt.return_value = None
    else:
        mock_jwt.side_effect = NoAuthorizationError()

    if status_code == 200:
        mock_profile.return_value = {
            'id': 1,
            'username': 'username',
            'full_name': 'full_name',
            'phone_number': 'phone_number',
            'avatar': 'avatar',
            'email': 'email',
            'is_active': True,
        }
    elif errors is not ValidationError:
        mock_profile.side_effect = errors

    response = client.get('/api/user/profile')
    assert response.status_code == status_code
    assert 'message' in response.json
    assert 'status' in response.json
    if status_code == 200:
        mock_profile.assert_called_once()
        assert 'data' in response.json
        assert 'id' in response.json['data']
        assert 'username' in response.json['data']
        assert 'full_name' in response.json['data']
        assert 'phone_number' in response.json['data']
        assert 'avatar' in response.json['data']
        assert 'email' in response.json['data']
        assert 'is_active' in response.json['data']


@pytest.mark.parametrize('is_authenticated, username, full_name,  phone, has_image, errors, status_code', [
    # Success
    (True, 'test', 'Tester', "0899521652", 'file', None, 200),
    (True, 'test', 'Tester', "0899521652", 'url', None, 200),
    (True, 'test', 'Tester', "0899521652", None, None, 200),

    # Error
    (True, None, 'Tester', "0899521652", None, ValidationError, 400),
    (True, 'test', None, "0899521652", None, ValidationError, 400),
    (True, 'test', 'Tester', None, None, ValidationError, 400),
    (False, 'test', 'Tester', "0899521652", None, None, 401),
    (True, 'test', 'Tester', "08990", None, ValidationError, 400),
    (True, 'test', 'Tester', "089900", None, ValidationError, 400),
    (True, 'test', 'Tester', "0899000000000000000000000", None, ValidationError, 400),
    (True, 'test', 'Tester', "0899521652", None, ExistingUserError, 409),
    (True, 'test', 'Tester', "0899521652", 'file', ValidationError, 400),
])
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('app.utils.validation.upload')
@patch('app.api.user_api.user_service.update')
def test_update_profile(mock_update, mock_cloudinary, mock_jwt, is_authenticated, username, full_name, phone, has_image,
                        errors, status_code, client):
    if is_authenticated:
        mock_jwt.return_value = None
    else:
        mock_jwt.side_effect = NoAuthorizationError()

    if errors != ValidationError and has_image:
        mock_cloudinary.return_value = {
            "secure_url": "http://res.cloudinary.com/demo/image/upload/fake-avatar.jpg",
            "public_id": "avatars/fake-avatar-123"
        }
    elif errors == ValidationError and has_image:
        mock_cloudinary.side_effect = Exception()

    payload = {}
    if username is not None:
        payload['username'] = username
    if full_name is not None:
        payload['full_name'] = full_name
    if phone is not None:
        payload['phone_number'] = phone

    if has_image == 'file':
        payload['avatar'] = (io.BytesIO(b"fake image blob"), "avatar.png")
    elif has_image == 'url':
        payload['avatar'] = "https://res.cloudinary.com/demo/image/upload/fake-avatar.jpg"


    if status_code == 200:
        mock_update.return_value = {
            'id': 1,
            'username': username,
            'full_name': full_name,
            'phone_number': phone,
            'avatar': "https://res.cloudinary.com/demo/image/upload/fake-avatar.jpg",
            'email': 'email',
            'is_active': True,
        }
    elif errors != ValidationError:
        mock_update.side_effect = errors
    else:
        mock_update.return_value = None

    response = client.put('/api/user/profile', data=payload, content_type='multipart/form-data')
    assert response.status_code == status_code
    if status_code == 200:
        if has_image == 'file': mock_cloudinary.assert_called_once()
        mock_update.assert_called_once()
        assert 'data' in response.json
        assert 'message' in response.json
        assert 'status' in response.json


@pytest.mark.parametrize('is_authenticated, status_code', [
    (True, 200),
    (False, 401),
])
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
def test_logout_api(mock_jwt, client, is_authenticated, status_code):
    if is_authenticated:
        mock_jwt.return_value = None
    else:
        mock_jwt.side_effect = NoAuthorizationError()

    client.set_cookie('access_token_cookies', 'access_token')
    client.set_cookie('refresh_token_cookies', 'refresh_token')

    response = client.get('/api/user/logout')
    assert response.status_code == status_code
    if status_code == 200:
        assert 'message' in response.json
        assert 'status' in response.json
        cookies = response.headers.getlist('Set-Cookie')
        assert any(
            'access_token_cookie=' in c and ('expires=' in c.lower() or 'Max-Age=0' in c) for c in cookies) is True
        assert any(
            'refresh_token_cookie=' in c and ('expires=' in c.lower() or 'Max-Age=0' in c) for c in cookies) is True

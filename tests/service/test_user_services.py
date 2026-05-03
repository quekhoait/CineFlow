import copy
import pytest
from unittest.mock import MagicMock, patch
from authlib.oauth2 import OAuth2Error
from flask_jwt_extended import create_refresh_token, decode_token
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, models, cache
from app.models import User, UserAuthMethod
from app.services import user_service
from app.services.user_service import send_otp, register
from app.utils.errors import (
    SendNotificationFailed, SendEmailFailed, ExistingUserError, InvalidOtpError, ExistingUsernameError, APIError,
    ExpiredOtpError, UserLoginEmailFailed, UserLoginGoogleFailed, UnauthorizedError
)

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
def setup_data():
    for i in range(1, 5):
        u = models.User(username=f'u{i}', password=generate_password_hash('Admin123@'),
                        full_name=f'u{i}', email=f'u{i}@gmail.com', role=models.RoleEnum.USER, is_active=True)
        db.session.add(u)
        db.session.flush()

        u_method = models.UserAuthMethod(user_id=u.id, provider="EMAIL", provider_id=u.email,
                                         refresh_token=create_refresh_token(str(u.id)))
        db.session.add(u_method)

    for i in range(5, 12):
        u = models.User(username=f'u{i}', full_name=f'u{i}', email=f'u{i}@gmail.com',
                        role=models.RoleEnum.USER, is_active=True)
        db.session.add(u)
        db.session.flush()

        u_method = models.UserAuthMethod(user_id=u.id, provider="GOOGLE", provider_id=f'{100000 + i}',
                                         refresh_token=create_refresh_token(str(u.id)))
        db.session.add(u_method)

    u12 = models.User(username='u12', password=generate_password_hash('Admin123@'),
                      full_name='u12', email='u12@gmail.com', role=models.RoleEnum.USER, is_active=True)
    db.session.add(u12)
    db.session.flush()

    m12_email = models.UserAuthMethod(user_id=u12.id, provider="EMAIL", provider_id=u12.email,
                                      refresh_token=create_refresh_token(str(u12.id)))
    m12_google = models.UserAuthMethod(user_id=u12.id, provider="GOOGLE", provider_id='100012',
                                       refresh_token=create_refresh_token(str(u12.id)))
    db.session.add_all([m12_email, m12_google])

    db.session.commit()


import pytest
from unittest.mock import patch, MagicMock

from app.services.user_service import send_otp
from app.utils.errors import SendNotificationFailed, ExistingUserError


@pytest.mark.parametrize("email, mail_failed, errors", [
    ('test@gmail.com', False, None),
    ('fail@gmail.com', True, SendNotificationFailed),
    ('u1@gmail.com', False, ExistingUserError),
    ('u5@gmail.com', False, None),
    ('u12@gmail.com', False, ExistingUserError),
])
@patch('app.pattern.notification.SendGridAPIClient')
def test_send_otp(mock_sendgrid, email, mail_failed, errors):

    mock_data = MagicMock()
    mock_data.email = email

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 202

    if mail_failed:
        mock_client.send.side_effect = Exception("Send failed")
    else:
        mock_client.send.return_value = mock_response

    mock_sendgrid.return_value = mock_client

    if errors:
        with pytest.raises(errors):
            send_otp(mock_data)
    else:
        send_otp(mock_data)

        mock_client.send.assert_called_once()

        saved_otp = cache.get(f'{email}')
        assert saved_otp is not None
        assert saved_otp.isdigit()
        assert len(saved_otp) == 6


@pytest.mark.parametrize("email, username , errors", [
    ("test@gmail.com", "tester", None),
    ("test@gmail.com", "tester", ExpiredOtpError),
    ("test@gmail.com", "tester", InvalidOtpError),
    ("test@gmail.com", "u1", ExistingUsernameError),
    ("u1@gmail.com", "tester", ExistingUserError),
    ("u5@gmail.com", 'tester', None),
    ("u12@gmail.com", 'tester', ExistingUserError),
    ("rollback@gmail.com", "rb_user", Exception),
])
@patch('app.services.user_service.RegisterRequest')
@patch('app.services.user_service.cache')
def test_register(mock_cache, mock_request, email, username, errors, monkeypatch):
    mock_data = MagicMock()
    mock_data.email = email
    mock_data.full_name = f'Tester Manager'
    mock_data.password = 'Abc123@'
    mock_data.username = username
    mock_data.otp = '256478'
    mock_data.phone_number = '+1555555555'
    mock_data.avatar = None
    mock_request.return_value = mock_data

    if errors is ExpiredOtpError:
        mock_cache.get.return_value = None
    elif errors is InvalidOtpError:
        mock_cache.get.return_value = '546789'
    else:
        mock_cache.get.return_value = mock_data.otp

    if errors:
        if errors is Exception:
            with patch('app.db.session.commit', side_effect=Exception("Database Error")):
                with pytest.raises(Exception):
                    register(mock_data)

                user = User.query.filter_by(email=email).first()
                assert user is None

        else:
            with pytest.raises(errors):
                register(mock_data)

            if errors not in [ExistingUserError, ExistingUsernameError]:
                user = User.query.filter_by(email=email).first()
                assert user is None

    else:
        register(mock_data)
        user = User.query.filter_by(email=email).first()
        assert user is not None
        assert user.username == mock_data.username
        assert user.full_name == mock_data.full_name
        assert check_password_hash(user.password, 'Abc123@')
        assert user.email == mock_data.email
        user_auth_method = UserAuthMethod.query.filter_by(user_id=user.id, provider="EMAIL").first()
        assert user_auth_method is not None
        assert user_auth_method.provider_id == mock_data.email
        mock_cache.delete.assert_called_once()


@pytest.mark.parametrize("provider, email, password, errors", [
    ("email", "u1@gmail.com", "Admin123@", None),
    ("email", "u13@gmail.com", "Admin123@", UserLoginEmailFailed),
    ("email", "u1@gmail.com", "Abc123@", UserLoginEmailFailed),
    ("google", None, None, None),
    ("abc_provider", None, None, ValueError),
])
@patch('app.pattern.provider.oauth')
@patch('app.pattern.provider.EmailLoginRequest')
def test_email_authenticate(mock_request, mock_oauth, provider, email, password, errors):
    if provider == 'email':
        mock_data = MagicMock()
        mock_data.email = email
        mock_data.password = password
        mock_request.return_value = mock_data

        if errors:
            with pytest.raises(errors):
                user_service.authenticate(provider, mock_data)
        else:
            raw_data = user_service.authenticate(provider, mock_data)
            assert raw_data is not None
            assert raw_data['access_token'] is not None
            assert raw_data['refresh_token'] is not None
            decoded_token = decode_token(raw_data['access_token'])
            user_id = decoded_token["sub"]
            user = db.session.get(User, user_id)
            assert user is not None
            assert user.email == mock_data.email
            user_auth_method = UserAuthMethod.query.filter_by(user_id=user.id).first()
            assert user_auth_method is not None
            assert user_auth_method.refresh_token == raw_data['refresh_token']
    else:
        fake_google_url = "https://accounts.google.com/o/oauth2/v2/auth?client_id=fake_id"
        mock_redirect_response = MagicMock()
        mock_redirect_response.headers = {'Location': fake_google_url}
        mock_oauth.google.authorize_redirect.return_value = mock_redirect_response
        if errors:
            with pytest.raises(errors):
                user_service.authenticate(provider, {})
        else:
            raw_data = user_service.authenticate(provider, {})
            assert raw_data is not None
            print(raw_data['url'])
            assert raw_data['url'] == fake_google_url


@pytest.mark.parametrize("provider, email, provider_id, has_user_info, errors", [
    ("google", "test@gmail.com", '25642589', True, None),
    ("google", "test@gmail.com", '25642589', False, None),
    ("google", "u1@gmail.com", '5648952', True, None),
    ("google", "u5@gmail.com", '100005', True, None),
    ("google", "u12@gmail.com", '100012', True, None),
    ("google", 'u12@gmail.com', '100012', True, UserLoginGoogleFailed),
])
@patch('app.pattern.provider.oauth')
def test_callback(mock_oauth, provider, email, provider_id, has_user_info, errors):
    user_data = {
        "email": email,
        "given_name": "test",
        "name": "tester",
        "sub": provider_id,
        "picture": "http://test.png",
    }

    if has_user_info:
        gg_response = {
            "access_token": "access_token",
            "userinfo": user_data,
        }
        mock_oauth.google.authorize_access_token.return_value = gg_response
    else:
        gg_response = {
            "access_token": "access_token",
        }
        mock_oauth.google.authorize_access_token.return_value = gg_response
        mock_resp = mock_oauth.google.get.return_value
        mock_resp.json.return_value = user_data

    if errors is UserLoginGoogleFailed:
        mock_oauth.google.authorize_access_token.side_effect = OAuth2Error()

    if errors:
        with pytest.raises(errors):
            user_service.callback(provider, {})

    else:
        raw_data = user_service.callback(provider, {})
        assert 'access_token' in raw_data
        assert 'refresh_token' in raw_data
        assert 'redirect' in raw_data

        if not has_user_info:
            mock_oauth.google.get.assert_called_once_with('https://openidconnect.googleapis.com/v1/userinfo')
        else:
            mock_oauth.google.get.assert_not_called()

        decoded_token = decode_token(raw_data['access_token'])
        user_id = decoded_token["sub"]
        user = db.session.get(User, user_id)
        assert user is not None
        assert user.email == email
        user_auth_method = UserAuthMethod.query.filter_by(user_id=user.id, provider=provider.upper()).first()
        assert user_auth_method is not None
        assert user_auth_method.provider_id == user_data['sub']
        assert user_auth_method.refresh_token == raw_data['refresh_token']


@pytest.mark.parametrize("user_id, provider, errors", [
    (1, 'email', None),
    (1, 'google', UnauthorizedError),
    (5, 'google', None),
    (12, 'google', None),
    (1, 'email', Exception),
])
def test_refresh(user_id, provider, errors, monkeypatch):
    user_real = db.session.get(User, user_id)
    user_auth_method = UserAuthMethod.query.filter_by(user_id=user_id, provider=provider.upper()).first()
    mock_current_user = MagicMock()
    mock_current_user.id = user_real.id
    mock_current_user.role = user_real.role
    monkeypatch.setattr('app.services.user_service.current_user', mock_current_user)
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = user_auth_method.refresh_token if user_auth_method else "hdsgadyuadsuad"
    monkeypatch.setattr('app.services.user_service.request', mock_request)
    old_token_string = user_auth_method.refresh_token if user_auth_method else None
    if errors:
        if errors is Exception:
            with patch('app.db.session.commit', side_effect=Exception("Database error")):
                with pytest.raises(Exception):
                    user_service.refresh()

                db.session.refresh(user_auth_method)
                assert user_auth_method.refresh_token == old_token_string

        else:
            with pytest.raises(errors):
                user_service.refresh()

            if user_auth_method:
                db.session.refresh(user_auth_method)
                assert user_auth_method.refresh_token == old_token_string
    else:
        result = user_service.refresh()
        new_auth_method = UserAuthMethod.query.filter_by(user_id=user_id, provider=provider.upper()).first()
        assert result is not None
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["refresh_token"] == new_auth_method.refresh_token

        if old_token_string:
            assert result["refresh_token"] != old_token_string


@pytest.mark.parametrize("user_id", [
    (1),
])
def test_profile(user_id, monkeypatch):
    user_real = db.session.get(User, user_id)
    monkeypatch.setattr('app.services.user_service.current_user', user_real)
    result = user_service.profile()
    assert result is not None
    assert result["id"] == user_real.id
    assert result["username"] == user_real.username


@pytest.mark.parametrize("user_id, username, errors", [
    (1, "new_username", None),
    (1, "u5", ExistingUserError),
    (1, "any_name", Exception),
])
def test_update(user_id, username, errors, monkeypatch):
    user_real = db.session.get(User, user_id)
    monkeypatch.setattr('app.services.user_service.current_user', user_real)
    mock_data = MagicMock()
    mock_data.username = username
    mock_data.full_name = "Tester"
    mock_data.phone_number = "123"
    mock_data.avatar = "https://avatars.githubusercontent.com/"
    old_user = copy.deepcopy(user_real)
    if errors:
        if errors is Exception:
            with patch('app.db.session.commit', side_effect=Exception("Database error")):
                with pytest.raises(Exception):
                    user_service.update(mock_data)

                db.session.refresh(user_real)
                assert user_real.username == old_user.username
                assert user_real.full_name == old_user.full_name

        else:
            with pytest.raises(errors):
                user_service.update(mock_data)

            db.session.refresh(user_real)
            assert user_real.username == old_user.username

    else:
        user_service.update(mock_data)
        update_user = db.session.get(User, user_id)
        assert update_user is not None
        assert update_user.full_name == mock_data.full_name
        assert update_user.phone_number == mock_data.phone_number
        assert update_user.avatar == mock_data.avatar
        assert update_user.username == mock_data.username
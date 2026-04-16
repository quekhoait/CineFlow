from unittest.mock import MagicMock, patch

import pytest
from authlib.oauth2 import OAuth2Error

from app import create_app, db
from app.pattern.provider import EmailProvider, GoogleProvider, AuthProvider
from app.utils.errors import UserLoginEmailFailed, UserLoginGoogleFailed


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

@pytest.mark.parametrize("provider_name, expected", [
    ("email", EmailProvider),
    ("EMAIL", EmailProvider),
    ("google", GoogleProvider),
    ("GOOGLE", GoogleProvider),
    ("unsupported_provider", ValueError),
])
def test_get_provider_success(provider_name, expected):
    if issubclass(expected, AuthProvider):
        provider = AuthProvider.get_provider(provider_name)
        assert isinstance(provider, expected)
    elif issubclass(expected, Exception):
        with pytest.raises(expected):
            AuthProvider.get_provider(provider_name)

@pytest.mark.parametrize("user_exists, pw_correct, updated_user ,expected", [
    (True, True, True, None),
    (False, True, True, UserLoginEmailFailed),
    (True, False, True, UserLoginEmailFailed),
    (True, True, False, Exception),
])
@patch('app.pattern.provider.create_access_token')
@patch('app.pattern.provider.create_refresh_token')
@patch('app.pattern.provider.check_password_hash')
@patch('app.pattern.provider.user_repo')
def test_email_provider_authenticate(mock_user_repo, mock_check_pass, mock_refresh, mock_access, user_exists, pw_correct, updated_user, expected):
    requests_data = {"email": "test@gmail.com", "password": "Abc123@"}
    response_data = {"access_token": "access123", "refresh_token": "refresh123"}
    if user_exists:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.password = "hashed_password"
        mock_user_repo.get_user_by_email.return_value = mock_user
    else:
        mock_user_repo.get_user_by_email.return_value = None

    mock_check_pass.return_value = pw_correct
    if not updated_user:
        mock_user_repo.update_user_auth_method.side_effect = Exception

    mock_access.return_value = response_data['access_token']
    mock_refresh.return_value = response_data['refresh_token']
    provider = AuthProvider.get_provider("email")
    if expected is None:
        result = provider.authenticate(requests_data)
        mock_user_repo.get_user_by_email.assert_called_with(requests_data["email"])
        mock_check_pass.assert_called_once_with("hashed_password", requests_data["password"])
        mock_user_repo.update_user_auth_method.assert_called_once_with(1, response_data['refresh_token'])
        assert result == response_data
    elif issubclass(expected, Exception):
        with pytest.raises(expected):
            provider.authenticate(requests_data)


@patch('app.pattern.provider.oauth')
@patch('app.pattern.provider.url_for')
def test_google_provider_authenticate(mock_url_for, mock_oauth):
    mock_url_for.return_value = "https://localhost:5000/callback"
    mock_redirect_response = MagicMock()
    mock_redirect_response.headers = {"Location": "https://accounts.google.com/o/oauth2/v2/auth"}
    mock_oauth.google.authorize_redirect.return_value = mock_redirect_response
    raw_data = {"url":mock_redirect_response.headers['Location']}
    provider = AuthProvider.get_provider("google")
    response = provider.authenticate({})
    mock_url_for.assert_called_once_with('api.user.callback', provider='google', _external=True)
    assert response == raw_data

@pytest.mark.parametrize("google_err,existed_user, existed_user_auth, expected", [
    (False, False, False, None),
    (True, False, False, UserLoginGoogleFailed),
    (False, True, False, None),
    (False, True, True, None),
])
@patch('app.pattern.provider.create_access_token')
@patch('app.pattern.provider.create_refresh_token')
@patch('app.pattern.provider.user_repo')
@patch('app.pattern.provider.oauth')
def test_google_callback_authenticate(mock_oauth, mock_user_repo,mock_refresh, mock_access, google_err, existed_user, existed_user_auth, expected):
    requests_data = {
        "userinfo": {
            "email": "test@gmail.com",
            "given_name": "test",
            "name": "tester",
            "sub": "2564859",
            "picture": "http://test.png",
        }
    }

    if google_err:
        mock_oauth.google.authorize_access_token.side_effect = OAuth2Error
    else:
        mock_oauth.google.authorize_access_token.return_value = requests_data


    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.name = 'tester'
    if existed_user:
        mock_user_repo.get_user_by_email.return_value = mock_user
    else:
        mock_user_repo.get_user_by_email.return_value = None
        mock_user_repo.create_user_google.return_value = mock_user

    if existed_user_auth:
        mock_user_repo.get_user_id_by_provider_id.return_value = 1
    else:
        mock_user_repo.get_user_by_provider_id.return_value = None

    response_data = {"access_token": "access123", "refresh_token": "refresh123"}
    mock_access.return_value = response_data['access_token']
    mock_refresh.return_value = response_data['refresh_token']

    provider = AuthProvider.get_provider("google")
    mock_request = MagicMock()

    if expected:
        with pytest.raises(expected):
            provider.callback(mock_request)
    else:
        result = provider.callback(mock_request)
        if existed_user:
            assert not mock_user_repo.create_user_google.called
        else:
            mock_user_repo.create_user_google.assert_called_once()

        if existed_user_auth:
            assert not mock_user_repo.create_user_auth_method.called
        else:
            mock_user_repo.create_user_auth_method.assert_called_once()

        mock_user_repo.update_user_auth_method.assert_called_once_with(1, "refresh123")
        assert result == response_data


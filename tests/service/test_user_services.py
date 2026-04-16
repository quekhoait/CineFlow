from types import SimpleNamespace

import pytest
from unittest.mock import MagicMock, patch
from werkzeug.security import check_password_hash
from app import db, cache, create_app
from app.dto.user_dto import OPTRequest, RegisterRequest
from app.services import user_service
from app.services.user_service import send_otp
from app.utils.errors import (
    SendEmailFailed, ExistingUserError, SendNotificationFailed,
    ExistingUsernameError, InvalidOtpError, ExpiredOtpError
)


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


@pytest.mark.parametrize("email, user_exist, user_auth_exist, mail_fails, expected", [
    ("test@gmail.com", False, False, False, None),
    ("test@gmail.com", True, False, False, None),
    ("test@gmail.com", True, True, False, ExistingUserError),
    ("test@gmail.com", False, False, True, SendNotificationFailed),
])
@patch('app.services.user_service.EmailSender')
@patch('app.services.user_service.user_repo')
def test_send_otp(MockUserRepo, MockEmailSender, email, user_exist, user_auth_exist, mail_fails, expected):
    req = OPTRequest().load({"email": email})
    MockUserRepo.get_user_id_by_email.return_value = 99 if user_exist else None
    MockUserRepo.get_user_by_provider_id.return_value = 99 if user_auth_exist else None
    mock_sender_instance = MockEmailSender.return_value

    if mail_fails:
        mock_sender_instance.send.side_effect = SendEmailFailed(email)

    if expected:
        with pytest.raises(expected):
            send_otp(req)

        if expected == SendNotificationFailed:
            assert cache.get(f"{email}") is None
    else:
        send_otp(req)
        mock_sender_instance.send.assert_called_once()
        params = mock_sender_instance.send.call_args[1]

        assert params["recipient"] == email

        saved_otp = cache.get(email)
        assert saved_otp is not None
        assert saved_otp.isdigit()
        assert len(saved_otp) == 6


@pytest.mark.parametrize("email_exist, username_exist, cache_otp, repo_err, expect_error", [
    (False, False, "123456", False, None),
    (True, False, "123456", False, ExistingUserError),
    (False, True, "123456", False, ExistingUsernameError),
    (False, False, None, False, ExpiredOtpError),
    (False, False, "253465", False, InvalidOtpError),
    (False, False, "123456", True, Exception),
])
@patch('app.services.user_service.user_repo')
@patch('app.services.user_service.cache')
@patch('app.services.user_service.db')
def test_register(mock_db, mock_cache, mock_user_repo, email_exist, username_exist, cache_otp, repo_err, expect_error):
    password = "Abc123@"
    mock_data = RegisterRequest().load({
        "email": "test@gmail.com",
        "username": "testuser",
        "full_name": "testuser",
        "password": password,
        "otp": "123456",
        "phone_number": "0788654251",
        "avatar": None,
    })

    mock_user_repo.get_user_id_by_email.return_value = 99 if email_exist else None
    mock_user_repo.get_user_id_by_username.return_value = 99 if username_exist else None
    mock_cache.get.return_value = cache_otp

    mock_new_user = MagicMock()
    mock_new_user.id = 100
    mock_user_repo.create_user_email.return_value = mock_new_user

    if repo_err:
        mock_user_repo.create_user_email.side_effect = Exception

    if expect_error:
        with pytest.raises(expect_error):
            user_service.register(mock_data)

        assert not mock_db.session.commit.called
        if repo_err:
            assert mock_db.session.rollback.called

    else:
        user_service.register(mock_data)

        assert mock_user_repo.create_user_email.called
        args, _ = mock_user_repo.create_user_email.call_args
        data = args[0]

        assert check_password_hash(data.password, password)
        assert mock_user_repo.create_user_auth_method.called
        assert mock_cache.delete.called
        assert mock_db.session.commit.called


@pytest.mark.parametrize("provider_name, input_data, expected_result", [
    ("email", {"email": "test@gmail.com", "password": "123"}, "token_email_123"),
    ("google", {"code": "xyz_google_code"}, "redirect_google_url"),
])
@patch('app.services.user_service.AuthProvider')
def test_authenticate(mock_auth_provider, provider_name, input_data, expected_result):
    mock_provider_instance = MagicMock()
    mock_auth_provider.get_provider.return_value = mock_provider_instance
    mock_provider_instance.authenticate.return_value = expected_result

    result = user_service.authenticate(provider_name, input_data)
    mock_auth_provider.get_provider.assert_called_once_with(provider_name)
    mock_provider_instance.authenticate.assert_called_once_with(input_data)
    assert result == expected_result

@pytest.mark.parametrize("has_error", [
    False,
    True,
])
@patch('app.services.user_service.db')
@patch('app.services.user_service.AuthProvider')
def test_callback(mock_auth_provider, mock_db, has_error):
    provider_name = "google"
    mock_request = MagicMock()
    mock_provider_instance = MagicMock()
    mock_auth_provider.get_provider.return_value = mock_provider_instance

    if has_error:
        mock_provider_instance.callback.side_effect = Exception
    else:
        mock_provider_instance.callback.return_value = {"access_token": "token_123"}

    if has_error:
        with pytest.raises(Exception):
            user_service.callback(provider_name, mock_request)

        mock_db.session.rollback.assert_called_once()

    else:
        result = user_service.callback(provider_name, mock_request)
        mock_auth_provider.get_provider.assert_called_once_with(provider_name)
        mock_provider_instance.callback.assert_called_once_with(mock_request)
        assert result == {"access_token": "token_123"}
        mock_db.session.commit.assert_called_once()


@patch('app.services.user_service.UserResponse')
def test_profile(mock_user_response):
    mock_current_user = MagicMock()
    mock_current_user.username = "test_user"
    mock_user_response().dump.return_value = {"username": "test_user"}
    with patch.dict(user_service.__dict__, {'current_user': mock_current_user}):
        result = user_service.profile()
    mock_user_response().dump.assert_called_once_with(mock_current_user)
    assert result == {"username": "test_user"}


@patch('app.services.user_service.create_refresh_token')  # Thêm patch này
@patch('app.services.user_service.create_access_token')
def test_refresh(mock_create_access_token, mock_create_refresh_token):
    mock_current_user = MagicMock()
    mock_current_user.id = 99

    mock_create_access_token.return_value = "new_access_123"
    mock_create_refresh_token.return_value = "new_refresh_456"

    with patch.dict(user_service.__dict__, {'current_user': mock_current_user}):
        result = user_service.refresh()

    mock_create_access_token.assert_called_once_with(identity=99)
    mock_create_refresh_token.assert_called_once_with(identity=99)

    assert result == {
        "access_token": "new_access_123",
        "refresh_token": "new_refresh_456"
    }


@pytest.mark.parametrize("changed_username, existing_username, db_error, expected_error", [
    (False, False, False, None),
    (True, False, False, None),
    (True, True, False, ExistingUserError),
    (False, False, True, Exception),
])
@patch('app.services.user_service.db')
@patch('app.services.user_service.UserResponse')
@patch('app.services.user_service.user_repo')
def test_update(mock_user_repo, mock_user_response, mock_db, changed_username, existing_username, db_error,
                expected_error):
    mock_data = SimpleNamespace(
        username="new_username",
        fullname="Tran B"
    )

    mock_current_user = MagicMock()
    mock_current_user.username = "old_username" if changed_username else mock_data.username
    mock_current_user.fullname = "Old Name"

    mock_user_repo.get_user_id_by_username.return_value = 99 if existing_username else None
    if db_error:
        mock_db.session.commit.side_effect = Exception()

    mock_user_response().dump.return_value = {"username": "new_username"}

    with patch.dict(user_service.__dict__, {'current_user': mock_current_user}):

        if expected_error:
            with pytest.raises(expected_error):
                user_service.update(mock_data)

            if db_error:
                mock_db.session.rollback.assert_called_once()

        else:
            result = user_service.update(mock_data)

            assert mock_current_user.username == mock_data.username
            assert mock_current_user.fullname == mock_data.fullname

            mock_db.session.add.assert_called_once_with(mock_current_user)
            mock_db.session.commit.assert_called_once()
            assert not mock_db.session.rollback.called
            assert result == {"username": "new_username"}
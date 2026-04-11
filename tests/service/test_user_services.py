from unittest.mock import MagicMock, patch
from parameterized import parameterized
from werkzeug.security import generate_password_hash, check_password_hash
from app import models, db, cache
from app.dto.user_dto import OPTRequest, RegisterRequest
from app.pattern.provider import AuthProvider
from app.services import user_service
from app.services.user_service import send_otp
from app.utils.errors import SendEmailFailed, ExistingUserError, SendNotificationFailed, ExistingUsernameError, \
    InvalidOtpError, ExpiredOtpError
from tests import BasicsTestCase

class TestUserServices(BasicsTestCase):
    def setUp(self):
        super(TestUserServices, self).setUp()
        self.mock_client = MagicMock()

    @parameterized.expand([
        ("test@gmail.com", False, False, None ),
        ("test@gmail.com", True, False, ExistingUserError),
        ("test@gmail.com", False,True,  SendNotificationFailed),
        ("test@gmail.com", True, True, ExistingUserError),
    ])
    @patch('app.services.user_service.EmailSender')
    @patch('app.services.user_service.user_repo')
    def test_send_otp(self, email, user_exist, mail_fails, expected, MockUserRepo, MockEmailSender ):
        req = OPTRequest().load({"email":email})
        MockUserRepo.get_user_id_by_email.return_value = 99 if user_exist else None
        mock_sender_instance = MockEmailSender.return_value

        if mail_fails: mock_sender_instance.send.side_effect = SendEmailFailed(email)

        if expected:
            with self.assertRaises(expected):
                send_otp(req)

            if expected == SendNotificationFailed:
                self.assertIsNone(cache.get(f"{email}"))

        else:
            send_otp(req)
            mock_sender_instance.send.assert_called_once()
            params = mock_sender_instance.send.call_args[1]
            self.assertEqual(params["recipient"], email)

            saved_otp = cache.get(email)
            self.assertIsNotNone(saved_otp)
            self.assertTrue(saved_otp.isdigit())
            self.assertEqual(len(saved_otp), 6)

    @parameterized.expand([
        (False, False, "123456",False, None),
        (True, False, "123456",False, ExistingUserError),
        (False, True, "123456",False, ExistingUsernameError),
        (False, False, None,False, ExpiredOtpError),
        (False, False, "253465",False, InvalidOtpError),
        (False, False, "123456", True, Exception),
    ])
    @patch('app.services.user_service.user_repo')
    @patch('app.services.user_service.cache')
    @patch('app.services.user_service.db')
    def test_register(self,email_exist,username_exist,cache_otp, repo_err, expect_error, mock_db, mock_cache, mock_user_repo):
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
            with self.assertRaises(expect_error):
                user_service.register(mock_data)

            self.assertFalse(mock_db.session.commit.called)
            if repo_err: self.assertTrue(mock_db.session.rollback.called)

        else:
            user_service.register(mock_data)
            self.assertTrue(mock_user_repo.create_user_email.called)
            args, _ = mock_user_repo.create_user_email.call_args
            data = args[0]
            self.assertTrue(check_password_hash(data.password, password))
            self.assertTrue(mock_user_repo.create_user_auth_method.called)
            self.assertTrue(mock_cache.delete.called)
            self.assertTrue(mock_db.session.commit.called)

    @patch('app.services.user_service.AuthProvider')
    def test_authenticate(self, mock_auth_provider):
        mock_provider_instance = MagicMock()
        expected_token = "fake_jwt_token_123"
        mock_provider_instance.authenticate.return_value = expected_token
        mock_auth_provider.get_provider.return_value = mock_provider_instance





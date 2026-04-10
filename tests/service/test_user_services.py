from unittest.mock import MagicMock, patch
from parameterized import parameterized
from werkzeug.security import generate_password_hash
from app import models, db, cache
from app.dto.user_dto import OPTRequest
from app.services.user_service import send_otp
from app.utils.errors import SendEmailFailed, ExistingUserError, SendNotificationFailed
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
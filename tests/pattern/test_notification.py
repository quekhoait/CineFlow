from unittest.mock import MagicMock
from parameterized import parameterized
from app.pattern.notification import EmailSender
from app.utils.errors import SendEmailFailed
from tests import BasicsTestCase


class NotifyTests(BasicsTestCase):
    def setUp(self):
        super().setUp()
        self.mock_mail_client = MagicMock()
        self.sender = EmailSender(self.mock_mail_client)

    @parameterized.expand([
        ({"recipient":"test@gmail.com", "subject": "Wellcome", "body": "Hello from the testing environment!", "attachments": [{"filename":"ticket.pdf","content_type": "application/pdf", "data": b"data_0011110"},]}, True, None),
        ({"recipient":"test@gmail.com", "body": "Hello from the testing environment!", "attachments": [{"filename":"ticket.pdf","content_type": "application/pdf", "data": b"data_0011110"},]}, True, None),
        ({"recipient":"test@gmail.com", "subject": "Wellcome", "attachments": [{"filename":"ticket.pdf","content_type": "application/pdf", "data": b"data_0011110"},]}, True, None),
        ({"recipient": "test02@gmail.com","subject": "Wellcome", "body": "Hello from the testing environment!"}, True, None),
        ({"recipient": "test@gmail.com", "subject": "Wellcome", "body": "Hello from the testing environment!","attachments": [{"filename": "ticket.pdf", "content_type": "application/pdf", "data": b"data_0011110"}, ]},False, SendEmailFailed),
    ])
    def test_send(self, request, success, expected):
        if not success:
            self.mock_mail_client.send.side_effect = SendEmailFailed

        if expected:
            with self.assertRaises(SendEmailFailed):
                self.sender.send(
                    recipient=request.get("recipient"),
                    subject=request.get("subject", "Notification from CineFlow"),
                    body=request.get("body", None),
                    attachments=request.get("attachments", [])
                )
        else:
            result = self.sender.send(
                    recipient=request.get("recipient"),
                    subject=request.get("subject", "Notification from CineFlow"),
                    body=request.get("body", None),
                    attachments=request.get("attachments", [])
                )
            self.assertTrue(result)
            self.mock_mail_client.send.assert_called_once()
            sent_message = self.mock_mail_client.send.call_args[0][0]

            self.assertEqual(sent_message.recipients, [request.get("recipient")])
            self.assertEqual(sent_message.subject, request.get("subject", "Notification from CineFlow"))
            self.assertEqual(sent_message.body, request.get("body", None))

            if request.get("attachments", None) is not None:
                self.assertEqual(len(sent_message.attachments), len(request["attachments"]))
                attached_file = sent_message.attachments[0]
                self.assertEqual(attached_file.filename, request.get('attachments')[0]["filename"])
                self.assertEqual(attached_file.content_type, request.get('attachments')[0]["content_type"])
                self.assertEqual(attached_file.data, request.get('attachments')[0]["data"])
            else:
                self.assertEqual(len(sent_message.attachments), 0)
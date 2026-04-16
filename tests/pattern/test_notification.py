import pytest
from unittest.mock import MagicMock

from app import create_app, db
from app.pattern.notification import EmailSender
from app.utils.errors import SendEmailFailed

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

@pytest.fixture
def setup_notification():
    mock_mail_client = MagicMock()
    sender = EmailSender(mock_mail_client)
    return mock_mail_client, sender


@pytest.mark.parametrize("req_data, success, expected", [
    ({"recipient": "test@gmail.com", "subject": "Wellcome", "body": "Hello from the testing environment!",
      "attachments": [{"filename": "ticket.pdf", "content_type": "application/pdf", "data": b"data_0011110"}, ]}, True,
     None),
    ({"recipient": "test@gmail.com", "body": "Hello from the testing environment!",
      "attachments": [{"filename": "ticket.pdf", "content_type": "application/pdf", "data": b"data_0011110"}, ]}, True,
     None),
    ({"recipient": "test@gmail.com", "subject": "Wellcome",
      "attachments": [{"filename": "ticket.pdf", "content_type": "application/pdf", "data": b"data_0011110"}, ]}, True,
     None),
    ({"recipient": "test02@gmail.com", "subject": "Wellcome", "body": "Hello from the testing environment!"}, True,
     None),
    ({"recipient": "test@gmail.com", "subject": "Wellcome", "body": "Hello from the testing environment!",
      "attachments": [{"filename": "ticket.pdf", "content_type": "application/pdf", "data": b"data_0011110"}, ]}, False,
     SendEmailFailed),
])
def test_send(setup_notification, req_data, success, expected):
    mock_mail_client, sender = setup_notification

    if not success:
        mock_mail_client.send.side_effect = SendEmailFailed

    if expected:
        with pytest.raises(SendEmailFailed):
            sender.send(
                recipient=req_data.get("recipient"),
                subject=req_data.get("subject", "Notification from CineFlow"),
                body=req_data.get("body", None),
                attachments=req_data.get("attachments", [])
            )
    else:
        result = sender.send(
            recipient=req_data.get("recipient"),
            subject=req_data.get("subject", "Notification from CineFlow"),
            body=req_data.get("body", None),
            attachments=req_data.get("attachments", [])
        )

        assert result is True
        mock_mail_client.send.assert_called_once()
        sent_message = mock_mail_client.send.call_args[0][0]

        assert sent_message.recipients == [req_data.get("recipient")]
        assert sent_message.subject == req_data.get("subject", "Notification from CineFlow")
        assert sent_message.body == req_data.get("body", None)

        if req_data.get("attachments", None) is not None:
            assert len(sent_message.attachments) == len(req_data["attachments"])
            attached_file = sent_message.attachments[0]
            assert attached_file.filename == req_data.get('attachments')[0]["filename"]
            assert attached_file.content_type == req_data.get('attachments')[0]["content_type"]
            assert attached_file.data == req_data.get('attachments')[0]["data"]
        else:
            assert len(sent_message.attachments) == 0
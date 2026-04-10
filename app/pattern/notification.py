from abc import ABC, abstractmethod
from flask_mail import Message
from typing import Optional, List, Dict, Any

from app.utils.errors import SendEmailFailed


class NotificationSender(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, body: str, attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        pass # pragma: no cover

class EmailSender(NotificationSender):
    def __init__(self, mail_client):
        self.mail_client = mail_client

    def send(self, recipient: str, subject: str, body: str, attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        msg = Message(
            subject=subject or "Notification from CineFlow",
            recipients=[recipient],
        )

        if body:
            msg.body = body

        if attachments:
            for file in attachments:
                msg.attach(
                    filename=file["filename"],
                    content_type=file["content_type"],
                    data=file["data"],
                )
        try:
            self.mail_client.send(msg)
            return True
        except Exception:
            raise SendEmailFailed()
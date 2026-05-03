from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from flask import current_app

from app.utils.errors import SendEmailFailed


class NotificationSender(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, body: str, attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        pass


class EmailSender(NotificationSender):
    def __init__(self):
        self.api_key = current_app.config["SENDGRID_API_KEY"]
        self.from_email = current_app.config["SENDGRID_FROM"]

    def send(self, recipient: str, subject: str, body: str, attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=recipient,
                subject=subject or "Notification from CineFlow",
                plain_text_content=body
            )

            if attachments:
                import base64
                attachment_list = []

                for file in attachments:
                    encoded_file = base64.b64encode(file["data"]).decode()

                    attachment = Attachment(
                        FileContent(encoded_file),
                        FileName(file["filename"]),
                        FileType(file["content_type"]),
                        Disposition("attachment")
                    )
                    attachment_list.append(attachment)

                message.attachment = attachment_list

            sg = SendGridAPIClient(self.api_key)
            sg.send(message)

        except Exception as e:
            raise e
import random

from werkzeug.security import generate_password_hash
from app import cache, mail, db
from app.dto.user_dto import RegisterRequest, OPTRequest, UserAuthMethodRequest
from app.pattern.notification import EmailSender
from app.pattern.provider import AuthProvider
from app.repository import user_repo
from app.utils.errors import *


def send_otp(data: OPTRequest):
    email = data.email
    if user_repo.get_user_id_by_email(email):
        raise ExistingUserError()

    otp = str(random.randint(100000, 999999))
    cache.set(f"{email}", otp)

    try:
        sender = EmailSender(mail)
        sender.send(
            recipient=email,
            subject="CineFlow OTP Verification Code",
            body=f"Hi there,\n\n" +
                 f"Your OTP verification code is: {otp}\n\n" +
                 f"This code will expire in 5 minutes. For your security, please do not share this code with anyone.\n\n" +
                 f"Best regards,\n\n" +
                 f"The CineFlow Team\n\n"
        )
    except Exception:
        cache.delete(f"{email}")
        raise SendNotificationFailed(message="Have a problem while sending your OTP")

def register(data: RegisterRequest):
    if user_repo.get_user_id_by_email(data.email):
        raise ExistingUserError("Email already exists")

    if user_repo.get_user_id_by_username(data.username):
        raise ExistingUserError("Username already exists")

    cached_otp = cache.get(f"{data.email}")
    if not cached_otp:
        raise InvalidOtpError("OTP has expired or does not exist")

    if str(cached_otp) != str(data.otp):
        raise InvalidOtpError("Incorrect OTP verification code")

    data.password = generate_password_hash(data.password)

    try:
        user_id = user_repo.create_user_email(data)

        data_auth_method = UserAuthMethodRequest()
        data_auth_method.user_id = user_id
        data_auth_method.provider = "EMAIL"
        data_auth_method.provider_id = data.email
        user_repo.create_user_auth_method(data_auth_method)

        _ = user_repo.get_user_id_by_email(data.email)
        cache.delete(f"{data.email}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception((str(e)))

def authenticate(provider: str, data):
    return AuthProvider.get_provider(provider).authenticate(data)





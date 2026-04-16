import random
from flask_jwt_extended import current_user, create_refresh_token
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from app import cache, mail, db, jwt
from app.dto.user_dto import RegisterRequest, OPTRequest, UserAuthMethodRequest, UserResponse, TokenResponse
from app.pattern.notification import EmailSender
from app.pattern.provider import AuthProvider
from app.repository import user_repo
from app.utils.errors import *

def send_otp(data: OPTRequest):
    email = data.email
    if user_repo.get_user_id_by_email(email):
        if user_repo.get_user_by_provider_id(email):
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
        raise ExistingUserError()

    if user_repo.get_user_id_by_username(data.username):
        raise ExistingUsernameError()

    cached_otp = cache.get(f"{data.email}")
    if not cached_otp:
        raise ExpiredOtpError()

    if str(cached_otp) != str(data.otp):
        raise InvalidOtpError()

    data.password = generate_password_hash(data.password)

    try:
        user = user_repo.create_user_email(data)

        data_auth_method = UserAuthMethodRequest()
        data_auth_method.user_id = user.id
        data_auth_method.provider = "EMAIL"
        data_auth_method.provider_id = data.email
        user_repo.create_user_auth_method(data_auth_method)

        _ = user_repo.get_user_id_by_email(data.email)
        cache.delete(f"{data.email}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def authenticate(provider: str, data):
    return AuthProvider.get_provider(provider).authenticate(data)

def callback(provider: str, request):
    try:
        db.session.commit()
        return AuthProvider.get_provider(provider).callback(request)
    except Exception as e:
        db.session.rollback()
        raise e

def refresh():
    user_id = int(current_user.id)
    new_access_token = create_access_token(identity=user_id, additional_claims={'roles': current_user.role.value})
    new_refresh_token = create_refresh_token(identity=user_id, additional_claims={'roles': current_user.role.value})
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }

def profile() -> UserResponse:
    return UserResponse().dump(current_user)

def update(data) -> UserResponse:
    if data.username != current_user.username and user_repo.get_user_id_by_username(data.username):
        raise ExistingUserError("Username already exists")

    data_dict = vars(data) if not isinstance(data, dict) else data
    for key, value in data_dict.items():
        if hasattr(current_user, key):
            setattr(current_user, key, value)

    try:
        db.session.add(current_user)
        db.session.commit()
        return UserResponse().dump(current_user)
    except Exception as e:
        db.session.rollback()
        raise e

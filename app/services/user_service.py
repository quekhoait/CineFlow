import random

from flask import request
from flask_jwt_extended import current_user, create_refresh_token
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from app import cache, mail, db
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
    user = user_repo.get_user_by_email(data.email)
    if user and user_repo.get_user_by_provider_id(data.email):
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
        if not user:
            user = user_repo.create_user_email(data)
        else:
            user.username = data.username
            user.full_name = data.full_name
            user.password = data.password

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
        res = AuthProvider.get_provider(provider).callback(request)
        db.session.commit()
        return res
    except Exception as e:
        db.session.rollback()
        raise e

def refresh():
    user_id = int(current_user.id)
    client_refresh_token = request.cookies.get('refresh_token_cookie')
    user_auth_method = user_repo.get_user_auth_method_by_refresh_token(user_id, client_refresh_token)
    if not user_auth_method:
        raise UnauthorizedError()
    try:
        new_access_token = create_access_token(identity=user_id, additional_claims={'roles': current_user.role.value})
        new_refresh_token = create_refresh_token(identity=user_id, additional_claims={'roles': current_user.role.value})
        user_auth_method.refresh_token = new_refresh_token
        db.session.commit()
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }
    except Exception as e:
        db.session.rollback()
        raise e

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

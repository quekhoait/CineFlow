from app import db
from app.dto.user_dto import RegisterRequest, UserAuthMethodRequest, UserResponse, GoogleAuthRequest
from app.models import User, UserAuthMethod

def get_user_by_user_id(user_id: int):
    user = User.query.filter_by(id=user_id).first()
    return user

def get_user_by_email(email: str) -> User:
    return User.query.filter_by(email=email).first()

def get_user_id_by_email(email: str) -> int:
    user = User.query.filter_by(email=email).first()
    return user.id if user else None

def get_user_id_by_username(username) -> int:
    user = User.query.filter_by(username=username).first()
    return user.id if user else None

def get_user_by_provider_id(provider_id: str) -> int:
    user_auth = UserAuthMethod.query.filter_by(provider_id=provider_id).first()
    return user_auth.user if user_auth else None

def create_user_email(data: RegisterRequest):
    new_user = User(email=data.email,
                    password=data.password,
                    username=data.username,
                    full_name=data.full_name,
                    phone_number=data.phone_number,
                    avatar=data.avatar
                    )
    db.session.add(new_user)
    db.session.flush()
    return new_user

def create_user_google(data: GoogleAuthRequest):
    new_user = User(email=data.email,
                    username=data.username,
                    full_name=data.full_name,
                    avatar=data.avatar
                    )
    db.session.add(new_user)
    db.session.flush()
    return new_user

def create_user_auth_method(data: UserAuthMethodRequest):
    new_user_auth_method = UserAuthMethod(
        user_id=data.user_id,
        provider=data.provider,
        provider_id=data.provider_id,
    )
    db.session.add(new_user_auth_method)
    db.session.flush()
    return new_user_auth_method

def update_user_auth_method(user_id: int, refresh_token: str, provider):
    user_auth_method = UserAuthMethod.query.filter_by(user_id=user_id, provider=provider).first()
    user_auth_method.refresh_token = refresh_token
    return user_auth_method

def get_user_auth_method_by_refresh_token(user_id: int, refresh_token: str):
    return UserAuthMethod.query.filter_by(user_id=user_id ,refresh_token=refresh_token).first()
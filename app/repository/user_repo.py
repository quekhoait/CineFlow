from app import db
from app.dto.user_dto import RegisterRequest, UserAuthMethodRequest, UserResponse, GoogleAuthRequest
from app.models import User, UserAuthMethod

def get_user_by_user_id(user_id: int) -> UserResponse:
    user = User.query.filter_by(id=user_id).first()
    return UserResponse().load(UserResponse().dump(user))

def get_user_by_email(email: str) -> User:
    return User.query.filter_by(email=email).first()

def get_user_id_by_email(email: str) -> int:
    user = User.query.filter_by(email=email).first()
    return user.id if user else None

def get_user_id_by_username(username) -> int:
    user = User.query.filter_by(username=username).first()
    return user.id if user else None

def get_user_id_by_provider_id(provider_id: str) -> int:
    auth_method = UserAuthMethod.query.filter_by(provider_id=provider_id).first()
    return auth_method.user_id if auth_method else None

def create_user_email(data: RegisterRequest) -> UserResponse:
    new_user = User(email=data.email,
                    password=data.password,
                    username=data.username,
                    full_name=data.full_name,
                    phone_number=data.phone_number,
                    avatar=data.avatar
                    )
    db.session.add(new_user)
    db.session.flush()
    new_user = UserResponse().dump(new_user)
    return UserResponse().load(new_user)

def create_user_google(data: GoogleAuthRequest) -> UserResponse:
    new_user = User(email=data.email,
                    username=data.username,
                    full_name=data.full_name,
                    avatar=data.avatar
                    )
    db.session.add(new_user)
    db.session.flush()
    new_user = UserResponse().dump(new_user)
    return UserResponse().load(new_user)

def create_user_auth_method(data: UserAuthMethodRequest) -> int:
    new_user_auth_method = UserAuthMethod(
        user_id=data.user_id,
        provider=data.provider,
        provider_id=data.provider_id,
    )
    db.session.add(new_user_auth_method)
    db.session.flush()
    return new_user_auth_method.id

def update_user_auth_method(user_id: int, refresh_token: str):
    user_auth_method = UserAuthMethod.query.filter_by(user_id=user_id).first()
    user_auth_method.refresh_token = refresh_token
    db.session.commit()


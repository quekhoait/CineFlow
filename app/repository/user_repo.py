from app import db
from app.dto.user_dto import RegisterRequest, UserAuthMethodRequest, UserResponse
from app.models import User, UserAuthMethod


def get_user_id_by_email(email) -> int:
    return User.query.filter_by(email=email).first()

def get_user_by_email(email: str) -> User:
    return User.query.filter_by(email=email).first()

def get_user_id_by_username(username) -> int:
    return User.query.filter_by(username=username).first()

def create_user_email(data: RegisterRequest) -> int:
    new_user = User(email=data.email,
                    password=data.password,
                    username=data.username,
                    full_name=data.full_name,
                    phone_number=data.phone_number,
                    avatar=data.avatar
                    )
    db.session.add(new_user)
    db.session.flush()
    return new_user.id

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


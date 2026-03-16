from app import db
from app.dto.user_dto import RegisterRequest, UserAuthMethodRequest
from app.models import User, UserAuthMethod


def get_user_id_by_email(email) -> int:
    return User.query.filter_by(email=email).first()

def create_user(data: RegisterRequest) -> int:
    new_user = User(email=data.email,
                    password=data.password,
                    username=data.username,
                    full_name=data.full_name,
                    phone_number=data.phone_number,
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

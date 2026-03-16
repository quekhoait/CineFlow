from app.models import User


def get_user_id_by_email(email) -> int:
    return User.query.filter_by(email=email).first().id
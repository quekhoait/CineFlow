from flask_jwt_extended import get_jwt_identity

from app import db
from app.repository import booking_repo
from app.utils.errors import UnauthorizedError


def cancel(id):

    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()

    try:
        booking_repo.update_booking_status(user_id, id, "CANCELED")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
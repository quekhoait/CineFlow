import threading
from datetime import datetime

import requests
from flask import url_for
from flask_jwt_extended import get_jwt_identity
from app import db
from app.repository import booking_repo
from app.utils.errors import UnauthorizedError, ExpiredError, TicketCanceledError

def cancel(code: str):
    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()
    data = booking_repo.get_basic_booking_by_code(user_id, code)
    diff = data.start_time - datetime.now()

    if data.status == "CANCELED":
        raise TicketCanceledError(message="This booking is already canceled!")

    if diff.total_seconds()/3600 < 2:
        raise ExpiredError(message='You are only allowed to perform any operations at least 2 hours before the show starts!')

    try:
        booking_repo.update_show_seats(user_id, code)
        booking_repo.update_booking_status(user_id, data.code, "CANCELED")
        if data.payment_status.value == "PAID":
            url = url_for('api.payment.refund',code=code, _external=True)
            payload = {
                "user_id": user_id,
            }
            thread = threading.Thread(target=lambda: requests.post(url, json=payload, timeout=10))
            thread.start()

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


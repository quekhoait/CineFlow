import threading
import uuid
from datetime import datetime

import requests
from flask import url_for
from flask_jwt_extended import get_jwt_identity
from app import db, Show, Ticket, Booking
from app.dto.booking_dto import BookingRequest, BookingSchema
from app.repository import booking_repo, user_repo
from app.utils.errors import UnauthorizedError, ExpiredError, TicketCanceledError, NotFoundError, TicketExistError


def create(data: BookingRequest):
    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()

    show = booking_repo.get_show_by_id(data)
    if not show:
        raise NotFoundError("Show not found!")

    ticket_booked = show.tickets
    code_ticket_booked = [t.seat_code for t in ticket_booked]
    if set(data.code_seats).issubset(set(code_ticket_booked)):
        raise TicketExistError()

    ticket_code_seat = [t.code for t in show.room.seats]
    if not set(data.code_seats).issubset(set(ticket_code_seat)):
        raise NotFoundError("Seats not found!")

    # get list type seat
    type_seat = [s.type.value for s in show.room.seats if s.code in data.code_seats]

    # get day in week
    day_type = 'WEEKEND' if show.start_time.isoweekday() >= 6 else "WEEKDAY"
    type_seat = [f'{t}_{day_type}' for t in type_seat]

    price = booking_repo.get_price_type_seats(type_seat)
    price_total = sum(price)

    booking = {
        "user_id": user_id,
        "code":"BK" + uuid.uuid4().hex[:6].upper(),
        "total_price": price_total,
    }
    try:
        new_booking = BookingSchema().load(booking)
        booking_repo.create_booking(new_booking)
        booking_repo.create_tickets(data, new_booking.code)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def get_bookings():
    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()
    bookings = [Booking.query.filter_by(user_id=user_id).all()]
    return bookings

def get_booking_by_code(code):
    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()

    booking = booking_repo.get_booking_by_code(user_id, code)

    return booking

def cancel(code):
    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()

    data = booking_repo.get_booking_by_code(user_id, code)
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


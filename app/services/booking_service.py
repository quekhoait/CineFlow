import threading
import uuid
from datetime import datetime
import requests
from flask import url_for, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.dto.booking_dto import BookingRequest, BookingSchema, SeatBookedResponse, BookingDetailResponse, \
    BookingsPageResponse
from app.repository import booking_repo, user_repo
from app.utils.errors import UnauthorizedError, TicketCanceledError, NotFoundError, TicketExistError, ExpiredError


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
        booking_repo.create_tickets(data, new_booking.code, price)
        db.session.commit()
        return {
            "code": new_booking.code,
        }
    except Exception as e:
        db.session.rollback()
        raise e

def get_bookings():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 5, type=int)
    bookings = booking_repo.get_all_bookings_by_user(user_id, page, per_page)
    if not bookings:
        return []
    return BookingsPageResponse().dump(bookings)



def get_booking_by_code(code):
    user_id = get_jwt_identity()
    booking = booking_repo.get_booking_by_code(user_id, code)
    if not booking:
        raise NotFoundError("Booking not found!")

    return BookingDetailResponse().dump(booking)

def get_seat_by_code(code):
    booking = booking_repo.get_seat_by_code(code)
    return SeatBookedResponse(many=True).dump(booking)

def cancel(code: str):
    user_id = get_jwt_identity()
    data = booking_repo.get_basic_booking_by_code(user_id, code)
    diff = data.start_time - datetime.now()

    if data.payment_status == "REFUNDED":
        raise TicketCanceledError(message="This booking was refunded!")

    if diff.total_seconds()/3600 < 2:
        raise ExpiredError(message='You are only allowed to perform any operations at least 2 hours before the show starts!')

    try:
        booking_repo.update_show_seats(user_id, code)
        booking_repo.update_booking_status(user_id, data.code, "CANCELED")
        if data.payment_status.value == "PAID":
            url = url_for('api.payment.refund', _external=True)
            payload = {
                "method": "momo",
                "booking_code": data.code
            }
            headers = {'Authorization': request.headers.get('Authorization')}
            thread = threading.Thread(target=lambda: requests.post(url, json=payload,headers=headers, timeout=10))
            thread.start()

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


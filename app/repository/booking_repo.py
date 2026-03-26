import datetime

from app import Booking, BookingStatus, db
from app.dto.booking_dto import BookingResponse
from app.utils.errors import NotFoundError

def get_basic_booking_by_code(user_id, booking_code) -> BookingResponse:
    booking = Booking.query.filter_by(user_id = user_id, code=booking_code).first()
    if not booking:
        raise NotFoundError("Not found booking in your booking list")
    re_booking = BookingResponse().load(BookingResponse().dump(booking))
    re_booking.start_time = booking.tickets[0].show.start_time
    re_booking.film_title = booking.tickets[0].show.film.title
    return re_booking

def get_booking_by_code(user_id:int, booking_code):
    return Booking.query.filter_by(user_id = user_id, code=booking_code).first()

def update_booking_status(user_id:int, booking_code: str, status: str):
    booking = Booking.query.filter_by(code=booking_code, user_id=user_id).first()
    if not booking:
        raise NotFoundError("Not found booking in your booking list")

    status = BookingStatus[status]
    booking.status = status
    db.session.add(booking)

def update_show_seats(user_id:int, booking_code: str):
    booking = Booking.query.filter_by(code=booking_code, user_id=user_id).first()
    if not booking:
        raise NotFoundError("Not found booking in your booking list")

    for ticket in booking.tickets:
        ticket.active = False
        db.session.add(ticket)
import datetime

from app import Booking, BookingStatus, db
from app.dto.booking_dto import BookingResponse
from app.utils.errors import NotFoundError

def get_booking_by_id(user_id, id) -> BookingResponse:
    booking = Booking.query.filter_by(user_id = user_id, id=id).first()
    if not booking:
        raise NotFoundError("Not found booking in your booking list")

    re_booking = BookingResponse()
    re_booking.start_time = booking.tickets[0].show.start_time
    re_booking.film_title = booking.tickets[0].show.film


def update_booking_status(user_id: int, booking_id: int, status: str):
    booking = Booking.query.filter_by(user_id=user_id, id=booking_id).first()
    if not booking:
        raise NotFoundError("Not found booking in your booking list")

    status = BookingStatus[status]
    booking.status = status
    db.session.add(booking)
    db.session.flush()
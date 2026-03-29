import datetime
from decimal import Decimal
from tokenize import Double

from app import db, Ticket
from app.models import Booking, BookingStatus, Show, Rules
from app.dto.booking_dto import BookingResponse, BookingRequest, BookingSchema
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

def get_show_by_id(data:BookingRequest):
    return Show.query.filter_by(id=data.id_show).first()

def get_price_type_seats(type_seats:list):
    price = [Rules.query.filter_by(name=t).first() for t in type_seats]
    if not price:
        raise NotFoundError(f"Don't have config {type_seats}")
    return [float(p.value) for p in price]

def create_booking(data: BookingSchema):
    new_booking = Booking(
        code = data.code,
        user_id = data.user_id,
        total_price = data.total_price,
    )
    db.session.add(new_booking)
    db.session.flush()

def create_tickets(data: BookingRequest, booking_code: str):
    new_tickets = [Ticket(booking_code=booking_code, show_id=data.id_show, seat_code=s) for s in data.code_seats]
    [db.session.add(t) for t in new_tickets]
    db.session.flush()
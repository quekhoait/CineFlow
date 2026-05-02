from app import db
from app.models import Booking, BookingStatus, Show, Rules, Ticket, Film, BookingPaymentStatus
from app.dto.booking_dto import BookingResponse, BookingRequest, BookingSchema
from app.utils.errors import NotFoundError, TicketExistError

from app.utils.errors import NotFoundError, TransactionComplete
from datetime import datetime

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

def get_all_bookings_by_user(user_id: int, page, per_page, code=None, film=None):
    bookings = Booking.query.filter_by(user_id=user_id)
    if code:
        bookings = bookings.filter(Booking.code == code)

    if film:
        bookings = bookings.join(Booking.tickets) \
            .join(Ticket.show) \
            .join(Show.film) \
            .filter(Film.title.ilike(f"%{film}%"))

    return bookings.order_by(Booking.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

def get_show_by_id(data:BookingRequest):
    return Show.query.filter_by(id=data.id_show).first()

def get_rules_by_names(rule_names: list):
    rules = Rules.query.filter(Rules.name.in_(rule_names)).all()
    if not rules or len(rules) != len(rule_names):
        raise NotFoundError(f"Missing price config for some seat types in {rule_names}")
    return rules


def check_and_lock_seats(show_id: int, code_seats: list):
    booked = (Ticket.query.filter(Ticket.show_id == show_id,Ticket.seat_code.in_(code_seats),Ticket.active == True)
              .with_for_update().all())
    if booked:
        raise TicketExistError()

def create_booking(data: BookingSchema):

    new_booking = Booking(
        code = data.code,
        user_id = data.user_id,
        total_price = data.total_price,
    )

    db.session.add(new_booking)
    db.session.flush()

def create_tickets(data: BookingRequest, booking_code: str, price):
    new_tickets = [Ticket(booking_code=booking_code, show_id=data.id_show, seat_code=s, price=price[i]) for (i,s) in enumerate(data.code_seats)]
    [db.session.add(t) for t in new_tickets]
    db.session.flush()

def get_seat_by_code(code):
    ticket = Ticket.query.filter_by(booking_code=code).all()
    if not ticket:
        raise NotFoundError(f"No booking found with code: {code}")
    return ticket

def get_bookings():
    return Booking.query.all()
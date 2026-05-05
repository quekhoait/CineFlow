import logging
import re
import threading
import uuid
from datetime import datetime, timedelta
import requests
from flask import url_for, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.dto.booking_dto import BookingRequest, BookingSchema, SeatBookedResponse, BookingDetailResponse, \
    BookingsPageResponse
from app.models import BookingStatus, PaymentStatus, BookingPaymentStatus
from app.repository import booking_repo
from app.utils.errors import UnauthorizedError, TicketCanceledError, NotFoundError, \
    ExpiredTicketError, CancelCheckedInTicketError, ExpiredError, LimitBookingError

def create(data: BookingRequest):
    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()

    if len(data.code_seats) > 8:
        raise LimitBookingError("Each person is only allowed to reserve a maximum of 8 seats per screening!")

    show = booking_repo.get_show_by_id(data)
    if not show:
        raise NotFoundError("Show not found!")

    if show.start_time <= datetime.now():
        raise ExpiredError(message="Tickets cannot be booked because this screening has already started!")

    booking_repo.check_and_lock_seats(show.id, data.code_seats)
    seat_dict = {s.code: s.type.value for s in show.room.seats}

    if not set(data.code_seats).issubset(set(seat_dict.keys())):
        raise NotFoundError("Seats not found in this room!")

    day_type = 'WEEKEND' if show.start_time.isoweekday() >= 6 else "WEEKDAY"

    unique_rule_names = list(set([f"{seat_dict[code]}_{day_type}" for code in data.code_seats]))

    rules = booking_repo.get_rules_by_names(unique_rule_names)
    rule_dict = {r.name: float(r.value) for r in rules}

    ordered_prices = [rule_dict[f"{seat_dict[code]}_{day_type}"] for code in data.code_seats]
    price_total = sum(ordered_prices)

    hold_minutes = rule_dict.get('HOLD_BOOKING', 10)
    expired_time = datetime.now() + timedelta(minutes=hold_minutes)

    if expired_time > show.start_time:
        expired_time = show.start_time

    booking = {
        "user_id": user_id,
        "code": "BK" + uuid.uuid4().hex[:6].upper(),
        "total_price": price_total,
        "expired_time": expired_time
    }

    try:
        new_booking = BookingSchema().load(booking)
        booking_repo.create_booking(new_booking)
        booking_repo.create_tickets(data, new_booking.code, ordered_prices)
        db.session.commit()

        return {
            "code": new_booking.code,
            "expired_time": expired_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        db.session.rollback()
        raise e

def get_bookings():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 5, type=int)
    q = request.args.get('q', None)
    pattern = r"^BK[A-Z0-9]{6}$"
    if q and re.match(pattern, q):
        bookings = booking_repo.get_all_bookings_by_user(user_id, page, per_page, code=q)
    elif q:
        bookings = booking_repo.get_all_bookings_by_user(user_id, page, per_page, film=q)
    else:
        bookings = booking_repo.get_all_bookings_by_user(user_id, page, per_page)

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

def cancel(code, method):
    user_id = get_jwt_identity()
    data = booking_repo.get_basic_booking_by_code(user_id, code)
    rules = booking_repo.get_rules_by_names(['CANCEL_HOUR'])
    rule_dict = {r.name: float(r.value) for r in rules}
    diff = data.start_time - datetime.now()

    if data.status.value == "CANCELED":
        raise TicketCanceledError()

    if data.check_in is not None:
        raise CancelCheckedInTicketError()

    if diff.total_seconds()/3600 < rule_dict['CANCEL_HOUR']:
        raise ExpiredTicketError()

    try:
        booking = booking_repo.get_booking_by_code(user_id, code)
        if not booking:
            raise NotFoundError("Not found booking in your booking list")
        for t in booking.tickets: t.active = False
        booking.status = BookingStatus.CANCELED
        if booking.payment_status.value == 'PAID':
            booking.payment_status = BookingPaymentStatus.REFUNDING
        else:
            booking.payment_status = BookingPaymentStatus.REFUNDED
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e

    try:
        if booking.payment_status.value == "REFUNDING":
            current_cookies = request.cookies.to_dict()
            url = url_for('api.payment.refund', _external=True)
            payload = {
                "method": method.lower(),
                "booking_code": data.code
            }
            header = {
                "X-CSRF-TOKEN": current_cookies.get('csrf_access_token')
            }
            thread = threading.Thread(
                target=lambda: requests.post(url, cookies=current_cookies, headers=header, json=payload, timeout=10))
            thread.start()
    except Exception as e:
        logging.error("Flow refund error after cancel. Let check it!")

def update_status_booking():
    booking = booking_repo.get_bookings()
    if booking:
        for b in booking:
            if b.expired_time and b.expired_time < datetime.now() and b.payment_status == BookingPaymentStatus.PENDING:
                b.status = BookingStatus.CANCELED
                b.payment_status = BookingPaymentStatus.REFUNDED
                for t in b.tickets: t.active = False

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
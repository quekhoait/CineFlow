from flask_jwt_extended import get_jwt_identity
from app import payment, db, BookingPaymentStatus
from app.dto.payment_dto import CreatePaymentResponse
from app.pattern.method_payment import PaymentContext
from app.repository import booking_repo
from app.utils.errors import UnauthorizedError, NotFoundError, NoPaymentsError, RefundedPaymentsError


def create(data):
    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()
    booking = booking_repo.get_basic_booking_by_code(user_id, data.booking_code)

    try:
        strategy = payment.get_strategy(data.method)
        res = strategy.create(data.booking_code, booking.total_price)
        db.session.commit()
        return CreatePaymentResponse().dump(res)
    except Exception as e:
        db.session.rollback()
        raise e

def callback(method:str, data):
    try:
        payment.callback(method, data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return e

def refund(data):
    user_id = get_jwt_identity()
    booking = booking_repo.get_booking_by_code(user_id, data.booking_code)
    if not booking:
        raise NotFoundError("Booking not found!")
    refund = [p for p in booking.payments if p.status.value == "SUCCESS" and p.type.value == "REFUND"]
    if refund:
        raise RefundedPaymentsError()

    trans_id = [p.transaction_id for p in booking.payments if p.status.value == "SUCCESS" and p.type.value == "PAYMENT"]
    if not trans_id:
        raise NoPaymentsError()

    amount = booking.total_price

    payload = {
        "transaction_id": trans_id[0],
        "amount": int(round(float(amount))),
        "description": "Refund ticket from CineFlow",
        "booking_code": booking.code,
    }
    try:
        result_code =  payment.refund(data.method, payload)
        if result_code == 0:
            booking.payment_status = BookingPaymentStatus.REFUNDED
            db.session.add(booking)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
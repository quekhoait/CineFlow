from datetime import datetime, timedelta

from flask_jwt_extended import get_jwt_identity

import app
from app import db
from app.dto.payment_dto import CreatePaymentResponse
from app.models import BookingPaymentStatus, PaymentStatus
from app.pattern.method_payment import PaymentContext
from app.repository import booking_repo, payment_repo
from app.utils.errors import UnauthorizedError, NotFoundError, NoPaymentsError, RefundedPaymentsError, PaymentsError, NoPaymentsMethod
from config import Config, DevelopmentConfig, ProductionConfig
from flask import current_app

def create(data):
    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()
    booking = booking_repo.get_basic_booking_by_code(user_id, data.booking_code)
    existing_payment = payment_repo.get_payment_by_booking_code(data.booking_code)
    if existing_payment:
        if existing_payment.status == PaymentStatus.SUCCESS:
            raise PaymentsError("This booking has already been paid.")
        if existing_payment.expired_time < datetime.now():
            raise PaymentsError("Transaction has expired. Please refresh the page or try again!")
        return CreatePaymentResponse().dump(existing_payment)
    try:
        context = current_app.payment_context
        strategy = context.get_strategy(data.method)
        res = strategy.create(data.booking_code, booking.total_price)
        db.session.commit()
        return CreatePaymentResponse().dump(res)
    except Exception as e:
        print(e)
        db.session.rollback()
        raise e

def callback(method:str, data):
    try:
        context = current_app.payment_context
        context.callback(method, data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def transaction(method:str, data):
    user_id = get_jwt_identity()
    if not user_id:
        raise UnauthorizedError()
    try:
        context = current_app.payment_context
        result = context.transaction(method, data)
        if result.get('resultCode') == 0:
            db.session.commit()
            return result
        return result
    except Exception as e:
        db.session.rollback()
        raise e


def refund(data):
    user_id = get_jwt_identity()
    booking = booking_repo.get_booking_by_code(user_id, data.booking_code)
    if not booking: raise NotFoundError("Booking not found!")
    if booking.payment_status.value != "REFUNDING": raise RefundedPaymentsError()
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
        context = current_app.payment_context
        result_code = context.refund(data.method, payload)
        if result_code == 0:
            booking.payment_status = BookingPaymentStatus.REFUNDED
            db.session.add(booking)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e
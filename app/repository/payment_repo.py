from datetime import datetime, timedelta

from app import db
from app.models import Payment, PaymentStatus
from app.dto.payment_dto import MomoPaymentCallbackRequest
from app.models.booking import PaymentType, BookingPaymentStatus
from app.utils.errors import NotFoundError, RefundedPaymentsError, PaymentsError


def create_new_payment_with_momo(booking_code, data):
    new_payment = Payment(
        code = data['orderId'],
        booking_code = booking_code,
        payment_method = "MOMO",
        expired_time = datetime.now() + timedelta(minutes=15),
        pay_url = data['payUrl'],
        amount = data['amount'],
    )
    db.session.add(new_payment)
    db.session.flush()

def update_payment_result_momo(data: MomoPaymentCallbackRequest):
    payment = Payment.query.filter_by(code=data.get('orderId'), booking_code=data.get('extraData')).first()
    if not payment:
        raise NotFoundError("Payment not found!!")
    if payment.expired_time < datetime.now():
        payment.status = PaymentStatus.FAILED
        db.session.commit()
        raise PaymentsError(f"Payment expired at {payment.expired_time}")
    payment.transaction_id = data.get('transId')
    payment.status = PaymentStatus.SUCCESS if data.get('resultCode') == 0 else PaymentStatus.FAILED
    payment.booking.payment_status = BookingPaymentStatus.PAID if data.get('resultCode') == 0 else BookingPaymentStatus.PENDING
    db.session.add(payment)

def create_refund_result_momo(booking_code, data):
    new_refund = Payment(
        code = data['orderId'],
        booking_code = booking_code,
        payment_method = "MOMO",
        amount = data['amount'],
        status = PaymentStatus.SUCCESS if data['resultCode'] == 0 else PaymentStatus.FAILED,
        type = PaymentType.REFUND
    )
    db.session.add(new_refund)
    db.session.flush()

def get_payment_by_booking_code(booking_code):
    payment = Payment.query.filter_by(booking_code = booking_code).first()
    return payment

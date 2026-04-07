from datetime import datetime, timedelta

from app import db, PaymentStatus
from app.models import Payment
from app.dto.payment_dto import MomoPaymentCallbackRequest
from app.models.booking import PaymentType, BookingPaymentStatus
from app.utils.errors import NotFoundError


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

def create_new_payment_with_stripe(booking_code, data):
    new_payment = Payment(
        code = data['orderId'],
        booking_code = booking_code,
        payment_method = "stripe",
        expired_time = datetime.now() + timedelta(minutes=15),
        pay_url = data['payUrl'],
        amount = data['amount'],
    )
    db.session.add(new_payment)
    db.session.flush()

def update_payment_result_momo(data: MomoPaymentCallbackRequest):
    payment = Payment.query.filter_by(code=data.orderId, booking_code=data.extraData).first()
    if not payment:
        raise NotFoundError("Payment not found!!")
    payment.transaction_id = data.transId
    payment.status = PaymentStatus.SUCCESS if data.resultCode == 0 else PaymentStatus.FAILED
    payment.booking.payment_status = BookingPaymentStatus.PAID if data.resultCode == 0 else BookingPaymentStatus.PENDING
    db.session.add(payment)


def update_payment_result_stripe(order_id,transId, status):
    payment = Payment.query.filter_by(code=order_id).first()
    if not payment:
        print(f"Không tìm thấy đơn hàng Stripe: {order_id}")
        return

    if status == "complete":
        payment.status = PaymentStatus.SUCCESS
        payment.booking.payment_status = BookingPaymentStatus.PAID
        payment.transaction_id = transId
    else:
        payment.status = PaymentStatus.FAILED
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

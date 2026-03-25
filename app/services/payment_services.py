from app.models.booking import PaymentStatus
from app.repository import payment_repo
from app.dto.payment_dto import PaymentResponse, PaymentReFund
from app.Momo import momo
from app import db
from app.utils.errors import *

def create_payment(data, booking_id) -> PaymentResponse:
    try:
        payment_req = momo.created_pay(booking_id=booking_id, amount=data.get('total_price'))
        payment = payment_repo.create(payment_req, booking_id)
        db.session.commit()
        return PaymentResponse().dump(payment)
    except Exception as e:
        db.session.rollback()
        raise Exception((str(e)))

def process_refund(payment_id) -> PaymentReFund:
    payment = payment_repo.get_payment_by_id(payment_id)
    if not payment:
        raise PaymentNotFound()
    if payment.status != PaymentStatus.SUCCESSFUL:
        raise InvalidPaymentStatus()
    if not payment.momo_trans_id:
        raise MissingTransactionId()
    try:
        payment_repo.update_status(payment_id, PaymentStatus.REFUNDED)
        return PaymentReFund().dump({
            "message": "Refund successful"
        })
    except Exception as e:

        raise APIError(message=str(e), status_code=500)


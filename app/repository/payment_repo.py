from app.models.booking import Payment, PaymentStatus
from datetime import datetime, timedelta
from app import db
def create(data, booking_id):
    payment = Payment(
        booking_id = booking_id,
        transaction_id = data.get('orderId'),
        amount = data.get('amount'),
        pay_url = data.get('payUrl'),
        status = PaymentStatus.PENDING,
        expired_time = datetime.now() + timedelta(minutes=15)
    )
    db.session.add(payment)
    return payment

def update_status(payment_id, status):
    payment = Payment.query.filter_by(id=payment_id).first()
    payment.status = status
    db.session.commit()
    return payment

def get_payment_by_id(id):
    return Payment.query.filter_by(id=id).first()
def get_payment_by_trans_id(transaction_id):
    return Payment.query.filter_by(transaction_id=transaction_id).first()
from app.models.booking import Payment, PaymentStatus
from datetime import datetime, timedelta
from app import db
def create(data, booking_id):
    print("data: ", data)
    print(booking_id)
    payment = Payment(
        booking_id = booking_id,
        transaction_id = data.get('orderId'),
        amount = data.get('amount'),
        pay_url = data.get('payUrl'),
        status = PaymentStatus.PENDING,
        expired_time = datetime.now() + timedelta(minutes=15)
    )
    db.session.add(payment)
    db.session.commit()
    return payment
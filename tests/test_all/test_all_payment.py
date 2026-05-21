from datetime import datetime, timedelta
import pytest

from app import db
from app.models import (
    Booking,
    Payment,
    PaymentStatus,
    PaymentType, BookingPaymentStatus, booking
)


@pytest.fixture(autouse=True)
def app_context():
    from app import create_app

    app = create_app("testing_fake")
    ctx = app.app_context()
    ctx.push()

    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture
def client(app_context):
    return app_context.test_client()


@pytest.fixture
def logged_in_user(mocker):

    mocker.patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        return_value=None
    )

    mocker.patch(
        "app.services.payment_service.get_jwt_identity",
        return_value=4
    )

    return 4


def test_payment_full_workflow(client, logged_in_user, mocker):
    booking_code = "BK_UNIQUE_999"
    payment_code = "PAY_UNIQUE_999"
    booking = Booking(
        code=booking_code,
        user_id=4,
        total_price=65000,
        status="BOOKED",
        payment_status="PENDING"
    )
    db.session.add(booking)
    payment = Payment(
        code=payment_code,
        booking_code=booking_code,
        payment_method="momo",
        amount=65000,
        status=PaymentStatus.PENDING,
        type=PaymentType.PAYMENT,
        expired_time=datetime.now() + timedelta(minutes=10)
    )
    db.session.add(payment)
    db.session.commit()
    #chữ ký
    mocker.patch(
        "app.pattern.method_payment.MomoPaymentStrategy._create_signature",
        return_value="matched_signature"
    )
    #callback
    callback_payload = {
        "orderId": payment_code,
        "resultCode": 0,
        "amount": 65000,
        "extraData": booking_code,
        "signature": "matched_signature"
    }
    callback_res = client.post(
        "/api/payments/momo/callback",
        json=callback_payload
    )
    assert callback_res.status_code == 200
    db.session.refresh(booking)
    db.session.refresh(payment)
    assert booking.payment_status == BookingPaymentStatus.PAID
    assert payment.status == PaymentStatus.SUCCESS
    #transaction
    trans_payload = {
        "orderId": payment_code
    }
    trans_res = client.post(
        "/api/payments/momo/transaction",
        json=trans_payload
    )
    assert trans_res.status_code == 200
    assert trans_res.json["status"] == "success"
    #refund
    mocker.patch(
        "app.services.payment_service.PaymentContext.refund",
        return_value=0
    )
    booking.payment_status = BookingPaymentStatus.REFUNDING
    db.session.add(booking)
    db.session.commit()
    refund_payload = {
        "booking_code": booking_code,
        "method": "momo",
    }
    refund_res = client.post(
        "/api/payments/refund",
        json=refund_payload
    )
    assert refund_res.status_code == 200
    db.session.refresh(booking)
    assert booking.payment_status == BookingPaymentStatus.REFUNDED
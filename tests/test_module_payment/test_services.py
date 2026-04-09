from app import Booking, BookingPaymentStatus
from app.dto.payment_dto import PaymentRequest
from app.services import payment_service
from app.utils.errors import TransactionComplete, NotFoundError, UnauthorizedError, NoPaymentsMethod
from tests.conftest import sample_films, sample_shows, sample_bookings, sample_tickets
import pytest
from marshmallow import ValidationError

#Test logic booking đã thanh toán ròi mà thanh toán tiếp
def test_logic_create_payment_success(mock_jwt, sample_shows,sample_films , sample_tickets,sample_bookings):
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    res = payment_service.create(data)
    assert "payUrl" in res

#Test logic booking đã thanh toán ròi mà thanh toán tiếp
def test_logic_create_payment_expired(mock_jwt, sample_bookings):
    payload = {
        "booking_code": "BK_PAID_3",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(TransactionComplete) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "Transaction completed"

# #Không tìm thấy booking
def test_logic_create_momo_payment_by_not_booking(mock_jwt, sample_bookings, sample_tickets):
    payload = {
        "booking_code": "BK_HHHHHH",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(NotFoundError) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "Not found booking in your booking list"

#Dữ liệu đầu vào bị trống
@pytest.mark.parametrize("payload, expected_msg", [
    ({}, "Missing data for required field"),
    ({"method": "momo"}, "Missing data for required field"),
    ({"booking_code": "BK_PAID_1"}, "Missing data for required field"),
])
def test_logic_create_momo_payment_missing_payload(mock_jwt, sample_bookings, payload, expected_msg):
    with pytest.raises(ValidationError) as excinfo:
        data = PaymentRequest().load(payload)
        payment_service.create(data)
    errors = excinfo.value.messages
    for field, msgs in errors.items():
        assert "Missing data for required field." in msgs

# #test thanh toán đơn hàng của user 4 với tài khoản user 5 (cả 2 đều có tài khoản)
def test_logic_create_payment_wrong_owner(mocker, sample_bookings):
    mocker.patch('app.services.payment_service.get_jwt_identity', return_value=5)
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(NotFoundError) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "Not found booking in your booking list"

#Thanh toán khi chưa đăng nhập
def test_logic_create_payment_not_login (mocker, sample_bookings):
    mocker.patch('app.services.payment_service.get_jwt_identity', return_value=None)
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "momo",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(UnauthorizedError) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "Unauthorized"

#Thanh toán vơí method ko hợp lệ
def test_logic_create_payment_invalid_method(mock_jwt, sample_bookings, sample_films, sample_tickets, sample_shows):
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "bitcoin",
    }
    data = PaymentRequest().load(payload)
    with pytest.raises(NoPaymentsMethod) as excinfo:
        payment_service.create(data)
    assert excinfo.value.message == "Payment method current is not supported."


def test_momo_callback_service_success(test_session, sample_bookings):
    payload = {
        "partnerCode": "MOMO",
        "orderId": "BK_PAID_3",
        "resultCode": 0,
        "amount": 50000,
        "transId": 123456789,
        "extraData": "",
    }
    payment_service.callback("momo", payload)
    test_session.commit()
    booking = Booking.query.filter_by(code="BK_PAID_3").first()
    print(booking)
    assert booking is not None
    assert booking.payment_status == BookingPaymentStatus.PAID
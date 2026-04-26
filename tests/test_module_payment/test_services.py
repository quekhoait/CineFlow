import json
from datetime import datetime, timedelta
from unittest.mock import patch

from app import Booking, BookingPaymentStatus, Payment, PaymentStatus
from app.dto.payment_dto import PaymentRequest, MomoPaymentCallbackRequest
from app.services import payment_service
from app.utils.errors import TransactionComplete, NotFoundError, UnauthorizedError, NoPaymentsMethod, \
    RefundedPaymentsError, PaymentsError, NoPaymentsError
from tests.conftest import sample_films,sample_payments, sample_shows, sample_bookings, sample_tickets
import pytest
from marshmallow import ValidationError
from app import db


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


def test_create_payment_existing_valid_payment(mocker):
    mocker.patch(
        "app.services.payment_service.get_jwt_identity",
        return_value=1
    )
    mock_booking = mocker.Mock()
    mock_payment = mocker.Mock()
    mock_payment.pay_url = "https://momo.vn/pay/old_link"
    mock_payment.code = "PAY_BK1"
    mock_payment.expired_time = datetime.now() + timedelta(minutes=10)

    mocker.patch(
        "app.services.payment_service.booking_repo.get_basic_booking_by_code",
        return_value=mock_booking
    )
    mocker.patch(
        "app.services.payment_service.payment_repo.get_payment_by_booking_code",
        return_value=mock_payment
    )
    payload = PaymentRequest().load({
        "booking_code": "BK_PAID_1",
        "method": "momo"
    })
    result = payment_service.create(payload)
    assert result["payUrl"] == mock_payment.pay_url
    assert result["orderId"] == "PAY_BK1"


def test_create_payment_existing_expired_payment(mocker):
    mocker.patch(
        "app.services.payment_service.get_jwt_identity",
        return_value=1
    )
    mock_booking = mocker.Mock()
    mock_payment = mocker.Mock()
    mock_payment.pay_url = "https://momo.vn/pay/old_link"
    mock_payment.code = "PAY_BK1"
    mock_payment.expired_time = datetime.now() - timedelta(minutes=10)

    mocker.patch(
        "app.services.payment_service.booking_repo.get_basic_booking_by_code",
        return_value=mock_booking
    )
    mocker.patch(
        "app.services.payment_service.payment_repo.get_payment_by_booking_code",
        return_value=mock_payment
    )
    payload = PaymentRequest().load({
        "booking_code": "BK_PAID_1",
        "method": "momo"
    })
    with pytest.raises(PaymentsError) as excinfo:
        payment_service.create(payload)
    assert "Transaction has expired" in  excinfo.value.message

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
    assert excinfo.value.message == "Payment method current is not supported"

#
def test_momo_callback_service_success(test_session, sample_bookings, sample_payments, mocker):
    mocker.patch(
        'app.pattern.method_payment.MomoPaymentStrategy._create_signature',
        return_value="mocked_signature"
    )
    payload = {
        "partnerCode": "MOMO",
        "orderId": "PAY_BK2",
        "resultCode": 0,
        "amount": 50000,
        "transId": 123456789,
        "extraData": "BK_PAID_2",
        "signature": "mocked_signature"
    }
    payment_service.callback("momo", payload)
    test_session.commit()
    booking = Booking.query.filter_by(code="BK_PAID_2").first()
    assert booking is not None
    assert booking.payment_status == BookingPaymentStatus.PAID

# @patch('app.repository.payment_repo.update_payment_result_momo')
# def test_momo_callback_service_error(mock_repo):
#     mock_repo.side_effect = Exception("Database connection failed")
#     with pytest.raises(Exception) as excinfo:
#         payment_service.callback("momo", {})
#     assert "Database connection failed" in str(excinfo.value)



def test_momo_callback_service_error(test_session, mocker):
        mocker.patch('app.pattern.method_payment.MomoPaymentStrategy.callback',side_effect=Exception("Database Error"))
        mock_rollback = mocker.patch.object(db.session, 'rollback')
        data = {"orderId": "PAY_BK1"}
        with pytest.raises(Exception) as excinfo:
            payment_service.callback("momo", data)
        assert str(excinfo.value) == "Database Error"
        mock_rollback.assert_called_once()

def test_momo_transaction_success(test_session, mock_jwt, sample_payments, sample_bookings):
    payload = {
        "partnerCode": "MOMO",
        "orderId": "PAY_BK3",
        "extraData": "BK_PAID_3",
        "resultCode": 0,
        "amount": 50000,
        "transId": "123456789"
    }
    payment_service.transaction("momo", payload)
    test_session.commit()
    booking = Booking.query.filter_by(code="BK_PAID_3").first()
    payment = Payment.query.filter_by(code="PAY_BK3").first()
    assert booking is not None
    assert booking.payment_status == BookingPaymentStatus.PAID
    assert payment.status == PaymentStatus.SUCCESS


def test_transaction_commits_on_success(test_session, mock_jwt, mocker, sample_payments):
    payload = {"resultCode": 0, "message": "Success"}
    mocker.patch('app.pattern.method_payment.MomoPaymentStrategy.transaction', return_value=payload)
    mock_commit = mocker.patch.object(db.session, 'commit')
    data = {"orderId": "PAY_BK1"}
    result = payment_service.transaction("momo", data)
    assert result.get('resultCode') == 0
    mock_commit.assert_called_once()


def test_transaction_rollbacks_on_exception(test_session, mock_jwt, mocker):
        mocker.patch('app.pattern.method_payment.MomoPaymentStrategy.transaction',side_effect=Exception("Database Error"))
        mock_rollback = mocker.patch.object(db.session, 'rollback')
        data = {"orderId": "PAY_BK1"}
        with pytest.raises(Exception) as excinfo:
            payment_service.transaction("momo", data)
        assert str(excinfo.value) == "Database Error"
        mock_rollback.assert_called_once()


def test_refund_success(test_session, mocker, sample_bookings, sample_payments):
    mocker.patch('app.services.payment_service.get_jwt_identity', return_value=4)
    booking = [b for b in sample_bookings if b.code == "BK_PAID_3"][0]
    mocker.patch('app.repository.booking_repo.get_booking_by_code', return_value=booking)
    mocker.patch('app.pattern.method_payment.MomoPaymentStrategy.refund', return_value=0)

    mock_commit = mocker.patch.object(db.session, 'commit')
    payload = {"booking_code": "BK_PAID_3", "method": "momo"}
    data = PaymentRequest().load(payload)
    payment_service.refund(data)
    # 4. Kiểm tra kết quả
    assert booking.payment_status == BookingPaymentStatus.REFUNDED
    mock_commit.assert_called_once()


def test_refund_error_booking(test_session, mock_jwt, sample_bookings, sample_payments):
    payload = {"booking_code": "BK_PAID_311", "method": "momo"}
    with pytest.raises(NotFoundError) as excinfo:
        data = PaymentRequest().load(payload)
        payment_service.refund(data)
    assert excinfo.value.message == "Booking not found!"

def test_refund_error_payment(test_session, mock_jwt, sample_bookings, sample_payments):
    payload = {"booking_code": "BK_PAID_4", "method": "momo"}
    with pytest.raises(RefundedPaymentsError) as excinfo:
        data = PaymentRequest().load(payload)
        payment_service.refund(data)
    assert excinfo.value.message == "Refunded payments"

def test_refund_no_transaction_id(mock_jwt, mocker,  sample_bookings, sample_payments):
    data = {"booking_code": "BK_PAID_1", "method": "momo"}
    with pytest.raises(NoPaymentsError) as excinfo:
        payment_service.refund(PaymentRequest().load(data))
    assert excinfo.value.message == "You don't have any payments"

def test_auth(test_session, mocker):
    mocker.patch(
        "app.services.payment_service.get_jwt_identity",
        return_value=None
    )
    payload = {"orderId": "BK_PAY", "method": "momo"}
    with pytest.raises(UnauthorizedError) as excinfo:
        payment_service.transaction("momo",payload)
    assert excinfo.value.message == "Unauthorized"



def test_refund_rollbacks_on_exception(test_session, mock_jwt, mocker, sample_payments):
    mocker.patch(
        'app.services.payment_service.PaymentContext.refund',
        side_effect=Exception("Database Error")
    )
    mock_rollback = mocker.patch.object(db.session, 'rollback')

    data = {"booking_code": "BK_PAID_3", "method": "momo"}
    data = PaymentRequest().load(data)
    with pytest.raises(Exception) as excinfo:
        payment_service.refund(data)
    print(excinfo)
    assert "Database Error" in str(excinfo.value)
    mock_rollback.assert_called_once()
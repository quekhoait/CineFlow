import pytest
from unittest.mock import patch

from app import PaymentStatus, Payment
from app.dto.payment_dto import PaymentRequest
from app.services import payment_service
from app.utils.errors import APIError
from app.utils.json import StatusResponse
from tests.conftest import sample_films, sample_bookings, sample_payments, sample_tickets, sample_shows
from app.models.booking import BookingPaymentStatus, Booking

# Mock response giả định từ MoMo Service
MOMO_CREATE_RESPONSE = {
    "payUrl": "https://test-payment.momo.vn/pay/gate",
}

#test tạo payment thành công
def test_create_momo_payment_success(client, mock_jwt, sample_bookings, sample_tickets, sample_films):
        with patch('app.services.payment_service.create') as mock_create:
            mock_create.return_value = MOMO_CREATE_RESPONSE
            payload = {
                "booking_code": "BK_PAID",
                "method": "momo",
            }
            response = client.post('/api/payments/create', json=payload)
            assert response.status_code == 201
            res_data = response.json
            assert res_data['status'] == 'success'
#
# #Thanh toán payment  còn 10s
def test_create_momo_payment_booking_by_10s(client, mock_jwt, sample_bookings, sample_tickets):
    with patch('app.services.payment_service.create') as mock_create:
        mock_create.return_value = MOMO_CREATE_RESPONSE
        payload = {
            "booking_code": "BK_CRITICAL",
            "method": "momo",
        }
        response = client.post('/api/payments/create', json=payload)
        assert response.status_code == 201
        res_data = response.json
        assert res_data['status'] == 'success'

# #booking đã thanh toán ròi, thanh toán tiếp booking đó
def test_create_momo_payment_error(client, mock_jwt, sample_bookings, sample_tickets):
        payload = {
            "booking_code": "BK_SUCCESS",
            "method": "momo",
        }
        response = client.post('/api/payments/create', json=payload)
        assert response.status_code == 400
        res_data = response.json
        assert res_data['status'] == 'error'
#
# #Không tìm thấy booking
def test_create_momo_payment_by_not_booking(client, mock_jwt, sample_bookings, sample_tickets):
        payload = {
            "booking_code": "BK_HHHHHH",
            "method": "momo",
        }
        response = client.post('/api/payments/create', json=payload)
        assert response.status_code == 404
        res_data = response.json
        assert res_data['status'] == 'error'
#

@patch('app.services.payment_service.create')
def test_payment_api_internal_error(mock_service, mock_jwt, client):
    mock_service.side_effect = Exception("Internal Server Error")
    response = client.post('/api/payments/create')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Internal Server Error" in response.json['message']


#Dữ liệu đầu vào bị trống
@pytest.mark.parametrize("payload, expected_msg", [
    ({}, "Missing data for required field"),
    ({"method": "momo"}, "Missing data for required field"),
    ({"booking_code": "BK_PAID_1"}, "Missing data for required field"),
    ({"booking_code": "", "method": "momo"}, "Missing data for required field"),
])
def test_create_momo_payment_invalid_payload(client, mock_jwt, payload, expected_msg):
    response = client.post('/api/payments/create', json=payload)
    assert response.status_code == 404
    res_data = response.json
    assert res_data['status'] == 'error'



#Thanh toán khi chưa đăng nhập
def test_create_payment_not_login (client, sample_bookings):
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "momo",
    }
    response = client.post('/api/payments/create', json=payload)
    assert response.status_code == 401

#Thanh toán vơí method ko hợp lệ
def test_create_payment_invalid_method(client, mock_jwt, sample_bookings, sample_films, sample_tickets, sample_shows):
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "bitcoin",
    }
    response = client.post('/api/payments/create', json=payload)
    assert response.status_code == 404







@patch('app.services.payment_service.transaction')
def test_transaction_success(mock_transaction, client, mock_jwt, sample_payments):
    mock_transaction.return_value = {"orderId": "PAY_BK2", "status": "SUCCESS"}

    payload = {"orderId": "PAY_BK2"}
    response = client.post('/api/payments/momo/transaction', json=payload)

    # ASSERT: Bây giờ response sẽ là một Response object thật của Flask
    assert response.status_code == 200
    assert response.json['data']['orderId'] == "PAY_BK2"


@patch('app.services.payment_service.transaction')
def test_transaction_api_error(mock_transaction, client, mock_jwt, sample_payments):
    mock_transaction.side_effect = APIError(message="Payment not found!!", status_code=404)
    response = client.post('/api/payments/momo/transaction', json={"orderId": "WRONG_ID"})
    assert response.status_code == 404
    assert response.json['status'] == 'error'
    assert response.json['message'] == "Payment not found!!"

@patch('app.services.payment_service.transaction')
def test_transaction_internal_error(mock_service, mock_jwt, client):
    mock_service.side_effect = Exception("Internal Server Error")
    response = client.post('/api/payments/momo/transaction')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Internal Server Error" in response.json['message']

@patch('app.services.payment_service.refund')
def test_refund_success(mock_refund, client, mock_jwt, sample_payments):
    mock_refund.return_value = {
        "refundId": "MOMO_REF_123",
        "amount": 50000,
        "resultCode": 0
    }
    payload = {
        "booking_code": "BK_PAID_2",
        "method": "momo",
    }
    response = client.post(
        '/api/payments/refund',
        json=payload,
        headers={"Authorization": "Bearer fake_token"}
    )

    # ASSERT
    assert response.status_code == 201
    assert response.json['status'] == 'success'
    assert response.json['data']['refundId'] == "MOMO_REF_123"

@patch('app.services.payment_service.refund')
def test_refund_validation_error(mock_refund, client, mock_jwt):
    payload = {
        "booking_code": "",
    }
    response = client.post(
        '/api/payments/refund',
        json=payload,
        headers={"Authorization": "Bearer fake_token"}
    )

    # ASSERT: Code của bạn trả về 400 và message "Invalid Input"
    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert response.json['message'] == "Invalid Input"


@patch('app.services.payment_service.refund')
def test_refund_api_error(mock_refund, client, mock_jwt, sample_payments):
    mock_refund.side_effect = APIError(message="Đơn hàng đã quá hạn hoàn tiền", status_code=409)
    payload = {
        "booking_code": "BK_OLD",
        "method":"momo",
    }
    response = client.post(
        '/api/payments/refund',
        json=payload,
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 409
    assert response.json['status'] == 'error'
    assert response.json['message'] == "Đơn hàng đã quá hạn hoàn tiền"

@patch('app.services.payment_service.create')
def test_refund_internal_error(mock_service, mock_jwt, client):
    mock_service.side_effect = Exception("Internal Server Error")
    response = client.post('/api/payments/refund')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Internal Server Error" in response.json['message']
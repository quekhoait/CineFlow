import pytest
from unittest.mock import patch
from app.utils.json import StatusResponse
from tests.conftest import sample_films, sample_bookings, sample_tickets, sample_shows
from app.models.booking import BookingPaymentStatus

# Mock response giả định từ MoMo Service
MOMO_CREATE_RESPONSE = {
    "payUrl": "https://test-payment.momo.vn/pay/gate",
}

#test tạo booking thành công
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
# #Thanh toán booking còn 10s
def test_create_momo_payment_booking_by_10s(client, mock_jwt, sample_bookings, sample_tickets):
    with patch('app.services.payment_service.create') as mock_create:
        mock_create.return_value = MOMO_CREATE_RESPONSE
        payload = {
            "booking_code": "BK_CRITICAL",
            "method": "momo",
        }
        response = client.post('/api/payments/create', json=payload)
        print(response.json)
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

#
# #Thanh toán booking đã hết hạn
# def test_create_momo_payment_booking_1(client, mock_jwt, sample_bookings, sample_tickets):
#     payload = {
#         "booking_code": "BK_EXPIRED",
#         "method": "momo",
#     }
#     response = client.post('/api/payments/create', json=payload)
#     print(response.json)
#     assert response.status_code == 400
#     res_data = response.json
#     assert res_data['status'] == 'error'

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

#
# #test thanh toán đơn hàng của user 4 với tài khoản user 5 (cả 2 đều có tài khoản)
def test_create_payment_wrong_owner(client, mocker, sample_bookings):
    mocker.patch('flask_jwt_extended.utils.get_jwt_identity', return_value=5)
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "momo",
    }
    response = client.post('/api/payments/create', json=payload)
    assert response.status_code == 401

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



#Test luồng callback
def test_momo_callback_success(client, test_session, sample_bookings):
    payload = {
        "partnerCode": "MOMO",
        "orderId": "BK_PAID_3",
        "resultCode": 0,
        "amount": 50000,
        "transId": 123456789,
        "extraData": "",
    }
    response = client.post('/api/payments/momo/callback', json=payload)
    assert response.status_code == 200
    from app.models import Booking
    booking = Booking.query.filter_by(code="BK_PAID_3").first()
    assert booking.payment_status == BookingPaymentStatus.PAID
#

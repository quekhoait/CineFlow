import pytest
from unittest.mock import patch
from app.utils.json import StatusResponse
from tests.conftest import sample_bookings
from app.models.booking import BookingPaymentStatus

# Mock response giả định từ MoMo Service
MOMO_CREATE_RESPONSE = {
    "payUrl": "https://test-payment.momo.vn/pay/gate",
}

# def test_create_momo_payment_success(client, mock_jwt, sample_bookings):
#         with patch('app.services.payment_service.create') as mock_create:
#             mock_create.return_value = MOMO_CREATE_RESPONSE
#             payload = {
#                 "booking_code": "BK_PAID",
#                 "method": "momo",
#             }
#             response = client.post('/api/payments/create', json=payload)
#             assert response.status_code == 201
#             res_data = response.json
#             assert res_data['status'] == 'success'
#
# #booking đã thanh toán ròi, thanh toaán tiếp booking đó
# def test_create_momo_payment_error(client, mock_jwt, sample_bookings):
#         payload = {
#             "booking_code": "BK_SUCCESS",
#             "method": "momo",
#         }
#         response = client.post('/api/payments/create', json=payload)
#         assert response.status_code == 400
#         res_data = response.json
#         assert res_data['status'] == 'error'
#
# #Không tìm thấy booking
# def test_create_momo_payment_by_not_booking(client, mock_jwt, sample_bookings):
#         payload = {
#             "booking_code": "BK_HHHHHH",
#             "method": "momo",
#         }
#         response = client.post('/api/payments/create', json=payload)
#         assert response.status_code == 404
#         res_data = response.json
#         assert res_data['status'] == 'error'
#
# #Thanh toán booking còn 10s
# def test_create_momo_payment_booking_by_10s(client, mock_jwt, sample_bookings):
#     with patch('app.services.payment_service.create') as mock_create:
#         mock_create.return_value = MOMO_CREATE_RESPONSE
#     payload = {
#         "booking_code": "BK_CRITICAL",
#         "method": "momo",
#     }
#     response = client.post('/api/payments/create', json=payload)
#     assert response.status_code == 201
#     res_data = response.json
#     assert res_data['status'] == 'success'
#
# #Thanh toán booking đã hết hạn
# def test_create_momo_payment_booking_1(client, mock_jwt, sample_bookings):
#     payload = {
#         "booking_code": "BK_EXPIRED",
#         "method": "momo",
#     }
#     response = client.post('/api/payments/create', json=payload)
#     assert response.status_code == 400
#     res_data = response.json
#     assert res_data['status'] == 'error'

#Dữ liệu đầu vào bị trống
# def test_create_momo_payment_missing_payload(client, mock_jwt, sample_bookings):
#     payload = {}
#     response = client.post('/api/payments/create', json=payload)
#     assert response.status_code == 404
#     res_data = response.json
#     assert res_data['status'] == 'error'
#
# #test thanh toán đơn hàng của user 4 với user 5 (cả 2 đều có tài khoản)
# def test_create_payment_wrong_owner_1(client, mocker, sample_bookings):
#     mocker.patch('flask_jwt_extended.utils.get_jwt_identity', return_value=5)
#     mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=None)
#     payload = {
#         "booking_code": "BK_PAID_1",
#         "method": "momo",
#     }
#     response = client.post('/api/payments/create', json=payload)
#     assert response.status_code == 404

#Thanh toán khi chưa đăng nhập
def test_create_payment_wrong_owner_1(client,  sample_bookings):
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "momo",
    }
    response = client.post('/api/payments/create', json=payload)
    assert response.status_code == 401

#Thanh toán vơí method ko hợp lệ
# def test_create_payment_invalid_method(client, mock_jwt, sample_bookings):
#     payload = {
#         "booking_code": "BK_PAID",
#         "method": "bit-coin",  # Method không hỗ trợ
#     }
#     response = client.post('/api/payments/create', json=payload)
#
#     assert response.status_code == 400



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

#Test luồng callback với amount wrong
def test_momo_callback_wrong_amount(client, test_session, sample_bookings):
    payload = {
        "partnerCode": "MOMO",
        "orderId": "BK_PAID_3",  # Đơn này giá 50.000đ trong fixture
        "resultCode": 0,
        "amount": 1,  # MoMo gửi về chỉ có 1đ (Sai số tiền)
        "transId": 123456789,
        "extraData": "",
        "signature": "fake_signature"
    }

    response = client.post('/api/payments/momo/callback', json=payload)
    assert response.status_code == 400
    test_session.expire_all()
    booking = Booking.query.filter_by(code="BK_PAID_3").first()
    assert booking.payment_status == BookingPaymentStatus.PENDING
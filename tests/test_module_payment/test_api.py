from datetime import datetime, timedelta, date, time


import pytest
from unittest.mock import patch

from marshmallow import ValidationError

from app.models import PaymentStatus, Payment, PaymentType, Ticket, Show, Film
from app.dto.payment_dto import PaymentRequest
from app.services import payment_service
from app.utils.errors import APIError, NoPaymentsMethod
from app.utils.json import StatusResponse
from app.models.booking import BookingPaymentStatus, Booking
from app import db

@pytest.fixture(autouse=True)
def app_context():
    from app import create_app
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()
    app_context.pop()

@pytest.fixture(autouse=True)
def client(app_context):
    return app_context.test_client()

@pytest.fixture(autouse=True)
def sample_films(app_context):
    today = date.today()

    films = [
        # --- PHIM 1: Đang chiếu (Bắt đầu từ 10 ngày trước, còn 20 ngày nữa mới hết) ---
        Film(
            id=1,
            title="Cuộc Chiến Đa Vũ Trụ",
            description="Một bộ phim hành động viễn tưởng đỉnh cao.",
            genre="Hành Động, Viễn Tưởng",
            age_limit=13,
            release_date=today - timedelta(days=10),
            expired_date=today + timedelta(days=20),
            poster="poster_multiverse.jpg",
            duration=120
        ),

        # --- PHIM 2: Đang chiếu (Sắp hết hạn - còn 2 ngày) ---
        Film(
            id=2,
            title="Hài Kịch Cuối Tuần",
            description="Những tình huống dở khóc dở cười.",
            genre="Hài Hước",
            age_limit=16,
            release_date=today - timedelta(days=30),
            expired_date=today + timedelta(days=2),
            poster="poster_comedy.jpg",
            duration=95
        ),

        # --- PHIM 3: Sắp chiếu (10 ngày nữa mới ra mắt) ---
        Film(
            id=3,
            title="Thám Tử Lừng Danh 2026",
            description="Phim trinh thám kịch tính.",
            genre="Trinh Thám",
            age_limit=18,
            release_date=today + timedelta(days=10),
            expired_date=today + timedelta(days=40),
            poster="poster_detective.jpg",
            duration=110
        ),

        # --- PHIM 4: Đã hết hạn chiếu (Đã kết thúc từ 5 ngày trước) ---
        Film(
            id=4,
            title="Ký Ức Đã Qua",
            description="Phim tình cảm lãng mạn.",
            genre="Tình Cảm",
            age_limit=13,
            release_date=today - timedelta(days=60),
            expired_date=today - timedelta(days=5),
            poster="poster_memory.jpg",
            duration=105
        )
    ]
    db.session.add_all(films)
    db.session.commit()

@pytest.fixture(autouse=True)
def sample_bookings(app_context):
    now = datetime(2026, 4, 7, 19, 15, 0)
    bookings = [
        # --- NHÓM 1: CÒN HẠN THANH TOÁN (Valid) ---
        Booking(
            code="BK_PAID_1",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=5),
            expired_time=now + timedelta(minutes=10)  # Còn 10 phút
        ),

        Booking(
            code="BK_PAID_2",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=5),
            expired_time=now + timedelta(minutes=10)  # Còn 10 phút
        ),
#Đ thành toán xong xuôi, gọi callback
        Booking(
            code="BK_PAID_3",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(minutes=5),
            expired_time=now + timedelta(minutes=10)  # Còn 10 phút
        ),

        Booking(
            code="BK_PAID_4",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="REFUNDED",
            created_at=now - timedelta(minutes=5),
            expired_time=now + timedelta(minutes=10)  # Còn 10 phút
        ),

        # --- NHÓM 2: SÁT NÚT HẾT HẠN (Critical) ---
        Booking(
            code="BK_CRITICAL",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=14, seconds=50),
            expired_time=now + timedelta(seconds=10)  # Chỉ còn 10 giây
        ),
        # --- NHÓM 3: ĐÃ QUÁ HẠN 15 PHÚT (Expired) ---
        # Điều kiện: expired_time < now
        Booking(
            code="BK_EXPIRED",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PENDING",
            created_at=now - timedelta(minutes=20),
            expired_time=now - timedelta(minutes=5)  # Đã hết hạn 5 phút trước
        ),
        # --- NHÓM 4: ĐÃ THANH TOÁN RỒI (Already Paid) ---
        Booking(
            code="BK_SUCCESS",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(hours=1),
            expired_time=now - timedelta(minutes=45)
        ),

        Booking(
            code="BK_OLD",
            user_id=4,
            total_price=50000,
            status="BOOKED",
            payment_status="PAID",
            created_at=now - timedelta(hours=1),
            expired_time=now - timedelta(minutes=45)
        )
    ]
    db.session.add_all(bookings)
    db.session.commit()

@pytest.fixture(autouse=True)
def sample_shows(app_context):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    shows = [
        # --- SUẤT CHIẾU HÔM NAY ---
        Show(
            id=1,
            start_time=datetime.combine(today, time(10, 0)),
            film_id=1, room_id=2
        ),
        Show(
            id=2,
            start_time=datetime.combine(today, time(12, 0)),
            film_id=2, room_id=1
        ),
        Show(
            id=3,
            start_time=datetime.combine(today, time(14, 0)),
            film_id=2, room_id=1
        ),
        Show(
            id=4,
            start_time=datetime.combine(today, time(20, 0)),
            film_id=2, room_id=1
        ),
        Show(
            id=5,
            start_time=datetime.combine(today, time(16, 0)),
            film_id=2, room_id=1
        ),
        # --- SUẤT CHIẾU NGÀY MAI ---
        Show(id=6,
            start_time=datetime.combine(tomorrow, time(14, 0)),
            film_id=1, room_id=1
        ),
        Show(
            id=7,
            start_time=datetime.combine(tomorrow, time(18, 0)),
            film_id=2, room_id=2
        )
    ]
    db.session.add_all(shows)
    db.session.commit()

@pytest.fixture(autouse=True)
def sample_payments(app_context):
    payments = [
        # Payment cho BK_PAID_1 (Đang chờ thanh toán)
        Payment(
            code="PAY_BK1",
            booking_code="BK_PAID_1",
            payment_method="momo",
            amount=50000,
            status=PaymentStatus.PENDING,
            type=PaymentType.PAYMENT,
            expired_time=datetime(2026, 4, 29, 21, 30, 0)
        ),

        # Payment cho BK_PAID_3 (Booking này bạn ghi chú là 'đã thanh toán xong xuôi')
        Payment(
            code="PAY_BK2",
            booking_code="BK_PAID_2",
            payment_method="momo",
            transaction_id="MOMO123456789",  # Giả lập đã có mã giao dịch
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT,
            expired_time = datetime(2026, 4, 29, 19, 30, 0)

    ),
        Payment(
            code="PAY_BK3",
            booking_code="BK_PAID_3",
            payment_method="momo",
            transaction_id="MOMO123456789",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT,
            expired_time=datetime(2026, 4, 16, 19, 30, 0)

        ),

        Payment(
            code="PAY_BK4",
            booking_code="BK_PAID_4",
            payment_method="momo",
            transaction_id="",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.REFUND,
            expired_time=datetime(2026, 4, 14, 19, 30, 0)

        ),

        # Payment cho BK_CRITICAL (Sắp hết hạn)
        Payment(
            code="PAY_CRITICAL",
            booking_code="BK_CRITICAL",
            payment_method="momo",
            amount=50000,
            status=PaymentStatus.PENDING,
            type=PaymentType.PAYMENT,
            expired_time=datetime(2026, 4, 14, 19, 15, 10)
        ),
        Payment(
            code="PAY_OLD",
            booking_code="BK_OLD",
            payment_method="momo",
            amount=50000,
            status=PaymentStatus.PENDING,
            type=PaymentType.PAYMENT,
            expired_time=datetime(2026, 4, 14, 19, 15, 10)
        ),
        Payment(
            code="PAY_SUCCESS_ENTRY",
            booking_code="BK_SUCCESS",
            payment_method="momo",
            amount=50000,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT,
            expired_time=datetime(2026, 4, 30, 0, 0, 0)
        )
    ]

    db.session.add_all(payments)
    db.session.commit()

@pytest.fixture(autouse=True)
def sample_tickets(app_context):
    # Dữ liệu Ticket tương ứng với các Booking trong sample_bookings
    tickets = [
        # Tickets cho BK_PAID_1 (Nhóm Valid - 2 vé cho đa dạng)
        Ticket(show_id=1, seat_code="A1", booking_code="BK_PAID_1", price=25000, active=True),
        Ticket(show_id=1, seat_code="A2", booking_code="BK_PAID_1", price=25000, active=True),

        # Ticket cho BK_PAID_2 (Nhóm Valid)
        Ticket(show_id=1, seat_code="B1", booking_code="BK_PAID_2", price=50000, active=True),

        # Ticket cho BK_PAID_3 (Nhóm Đã gọi callback)
        Ticket(show_id=1, seat_code="C1", booking_code="BK_PAID_3", price=50000, active=True),

        # Ticket cho BK_CRITICAL (Nhóm Sát nút hết hạn)
        Ticket(show_id=1, seat_code="D1", booking_code="BK_CRITICAL", price=50000, active=True),

        # Ticket cho BK_EXPIRED (Nhóm Đã hết hạn)
        Ticket(show_id=1, seat_code="E1", booking_code="BK_EXPIRED", price=50000, active=True),

        # Ticket cho BK_SUCCESS (Nhóm Đã thanh toán lâu rồi)
        Ticket(show_id=1, seat_code="F1", booking_code="BK_SUCCESS", price=50000, active=True)
    ]
    db.session.add_all(tickets)
    db.session.commit()

# Mock response giả định từ MoMo Service
MOMO_CREATE_RESPONSE = {
    "payUrl": "https://test-payment.momo.vn/pay/gate",
}

@pytest.fixture
def logged_in_user(mocker):
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=None)
    mocker.patch('flask_jwt_extended.get_jwt_identity', return_value=4)
    return 4

#test tạo payment thành công
def test_create_momo_payment_success(client, logged_in_user):
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
def test_create_momo_payment_booking_by_10s(client, logged_in_user):
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
#
# #booking đã thanh toán ròi, thanh toán tiếp booking đó
def test_create_momo_payment_error(client, mocker, logged_in_user):
    mock_create = mocker.patch('app.services.payment_service.create')
    mock_create.side_effect = APIError("Đã thanh toán", status_code=409)
    payload = {
        "booking_code": "BK_SUCCESS",
        "method": "momo",
    }
    response = client.post('/api/payments/create', json=payload)
    print(response.json)
    assert response.status_code == 409
    res_data = response.json
    assert res_data['status'] == 'error'

# # #Không tìm thấy booking
def test_create_momo_payment_by_not_booking(client, mocker, logged_in_user):
    mock_create = mocker.patch('app.services.payment_service.create')
    mock_create.side_effect = APIError("Đã thanh toán", status_code=409)
    payload = {
        "booking_code": "BK_HHHHHH",
        "method": "momo",
    }
    response = client.post('/api/payments/create', json=payload)
    assert response.status_code == 409
    res_data = response.json
    assert res_data['status'] == 'error'

def test_payment_api_internal_error(client, mocker, logged_in_user):
    mock_service = mocker.patch('app.services.payment_service.create')
    mock_service.side_effect = Exception("Internal Server Error")
    response = client.post('/api/payments/create')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Internal Server Error" in response.json['message']

@pytest.mark.parametrize("payload, expected_msg", [
    ({}, "Missing data for required field"),
    ({"method": "momo"}, "Missing data for required field"),
    ({"booking_code": "BK_PAID_1"}, "Missing data for required field"),
     # ({"booking_code": "", "method": "momo"}, "Missing data for required field"),
])
def test_create_momo_payment_invalid_payload(client, logged_in_user ,payload, expected_msg):
    response = client.post('/api/payments/create', json=payload)
    assert response.status_code == 404
    res_data = response.json
    assert res_data['status'] == 'error'
#
# #Thanh toán khi chưa đăng nhập
def test_create_payment_not_login (client):
    payload = {
        "booking_code": "BK_PAID_1",
        "method": "momo",
    }
    response = client.post('/api/payments/create', json=payload)
    assert response.status_code == 401
#
# #Thanh toán vơí method ko hợp lệ
def test_create_payment_invalid_method(client, logged_in_user):
    with patch('app.services.payment_service.create') as mock_create:
        mock_create.side_effect = NoPaymentsMethod("Payment method current is not supported")

        payload = {
            "booking_code": "BK_PAID_0",
            "method": "bit",
        }
        response = client.post('/api/payments/create', json=payload)

        # Bây giờ Controller sẽ nhảy vào khối 'except APIError' và trả về status_code của lỗi (404)
        assert response.status_code == 404
#callback
def test_callback_success(mocker, client):
    mock_callback = mocker.patch('app.services.payment_service.callback')
    mock_callback.return_value =None
    payload = {
        "orderId": "PAY_BK2",
        "resultCode": 0,
        "amount": 50000,
        "extraData": "BK_PAID_2"
    }
    response = client.post('/api/payments/momo/callback', json=payload)
    assert response.status_code == 200
    res_json = response.get_json()
    assert res_json['status'] == 'success'
    assert res_json['message'] == "Payment successful"

def test_callback_invalid(mocker, client):
    mock_callback = mocker.patch('app.services.payment_service.callback')
    errors = {"amount": ["Missing data for required field."]}
    mock_callback.side_effect = ValidationError(errors)
    payload = {
    }
    response = client.post('/api/payments/momo/callback', json=payload)
    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json['status'] == 'error'
    assert res_json['message'] == "Invalid Input"

def test_callback_api_error(mocker, client):
    mock_callback = mocker.patch('app.services.payment_service.callback')
    mock_callback.side_effect = APIError(message="Payment not found!!", status_code=404)
    response = client.post('/api/payments/momo/callback', json={"orderId": "WRONG_ID"})
    assert response.status_code == 404
    assert response.json['status'] == 'error'
    assert response.json['message'] == "Payment not found!!"

    #  ném ra APIError (giả sử 402 Payment Required)
def test_callback_api_error_402(mocker, client):
    mock_service = mocker.patch('app.services.payment_service.callback')
    mock_service.side_effect = APIError(message="Payment expired", status_code=402)
    response = client.post('/api/payments/momo/callback', json={"orderId": "WRONG_ID"})
    assert response.status_code == 402
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == "Payment expired"

    # Setup mock: ném ra một lỗi Python bất kỳ
def test_callback_internal_error(mocker, client):
    mock_service = mocker.patch('app.services.payment_service.callback')
    mock_service.side_effect = Exception("Database connection lost")
    response = client.post('/api/payments/momo/callback', json={"orderId": "WRONG_ID"})
    assert response.status_code == 500
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == "Internal Server Error"

def test_transaction_success(mocker, client, logged_in_user):
    mock_transaction = mocker.patch('app.services.payment_service.transaction')
    mock_transaction.return_value = {"orderId": "PAY_BK2", "status": "SUCCESS"}
    payload = {"orderId": "PAY_BK2"}
    response = client.post('/api/payments/momo/transaction', json=payload)
    assert response.status_code == 200
    assert response.json['data']['orderId'] == "PAY_BK2"
#
#
def test_transaction_api_error(mocker, client, logged_in_user):
    mock_transaction = mocker.patch('app.services.payment_service.transaction')
    mock_transaction.side_effect = APIError(message="Payment not found!!", status_code=404)
    response = client.post('/api/payments/momo/transaction', json={"orderId": "WRONG_ID"})
    assert response.status_code == 404
    assert response.json['status'] == 'error'
    assert response.json['message'] == "Payment not found!!"

def test_transaction_internal_error(mocker, client, logged_in_user):
    mock_service = mocker.patch('app.services.payment_service.transaction')
    mock_service.side_effect = Exception("Internal Server Error")
    response = client.post('/api/payments/momo/transaction')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Internal Server Error" in response.json['message']

def test_refund_success(mocker, client, logged_in_user):
    mock_refund = mocker.patch('app.services.payment_service.refund')
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
    assert response.status_code == 201
    assert response.json['status'] == 'success'
    assert response.json['data']['refundId'] == "MOMO_REF_123"
#
def test_refund_validation_error(mocker, client, logged_in_user):
    mocker.patch('app.services.payment_service.refund')
    payload = {
        "booking_code": "",
    }
    response = client.post(
        '/api/payments/refund',
        json=payload,
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert response.json['message'] == "Invalid Input"

#
def test_refund_api_error(mocker, client, logged_in_user):
    mock_refund  = mocker.patch('app.services.payment_service.refund')
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

#
def test_refund_internal_error(mocker, client, logged_in_user):
    mock_service = mocker.patch('app.services.payment_service.create')
    mock_service.side_effect = Exception("Internal Server Error")
    response = client.post('/api/payments/refund')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Internal Server Error" in response.json['message']
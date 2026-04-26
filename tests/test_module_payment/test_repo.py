from datetime import datetime, timedelta
import pytest
from app import Booking, PaymentStatus, BookingPaymentStatus, PaymentType
from app.dto.payment_dto import MomoPaymentCallbackRequest
from app.models import Payment
from app.repository import payment_repo
from app.utils.errors import PaymentsError, NotFoundError
from tests.conftest import sample_payments, sample_bookings


def test_create_new_payment_with_momo_success(test_session, sample_bookings):
    target_booking = "BK_PAID_1"
    momo_data = {
        'orderId': 'MOMO_REQ_789',
        'payUrl': 'https://test-payment.momo.vn/v2/gateway/redirect/xxx',
        'amount': 50000
    }
    payment_repo.create_new_payment_with_momo(target_booking, momo_data)
    new_payment = test_session.query(Payment).filter_by(code='MOMO_REQ_789').first()
    assert new_payment is not None
    assert new_payment.booking_code == target_booking
    assert new_payment.payment_method == "MOMO"
    assert new_payment.amount == 50000
    assert new_payment.pay_url == momo_data['payUrl']
    expected_expiry = datetime.now() + timedelta(minutes=15)
    diff = abs((new_payment.expired_time - expected_expiry).total_seconds())
    assert diff < 2

#kiểm tra mối quan he
def test_create_payment_linking_integrity(test_session, sample_bookings):
    target_code = "BK_CRITICAL"
    momo_data = {
        'orderId': 'MOMO_CRIT_001',
        'payUrl': 'https://momo.vn/pay',
        'amount': 50000
    }
    payment_repo.create_new_payment_with_momo(target_code, momo_data)
    payment = test_session.query(Payment).filter_by(code='MOMO_CRIT_001').first()
    booking = test_session.query(Booking).filter_by(code=target_code).first()

    assert payment.booking_code == booking.code

#NẾU MOMO TRẢ THIEUS DỮ LIỆU
def test_create_payment_with_missing_data_fields(test_session):
    invalid_data = {
        'orderId': 'FAIL_001'
        # Thiếu payUrl và amount
    }
    with pytest.raises(KeyError):
        payment_repo.create_new_payment_with_momo("BK_ANY", invalid_data)


def test_update_payment_success(test_session, sample_payments, sample_bookings):
    momo_update_data = {
        'orderId': 'PAY_BK1',
        'extraData': 'BK_PAID_1',
        'transId': 1111111,
        'amount': 50000,
        'resultCode': 0
    }
    payment_repo.update_payment_result_momo(momo_update_data)
    payment = test_session.query(Payment).filter_by(code='PAY_BK1').first()
    assert payment.status == PaymentStatus.SUCCESS
    assert payment.transaction_id == 1111111
    assert payment.booking.payment_status == BookingPaymentStatus.PAID

#momo báo lỗi, ko update dc
def test_update_payment_failed_from_momo(test_session, sample_payments):
    momo_update_data = {
        'orderId': 'PAY_BK1',
        'extraData': 'BK_PAID_1',
        'transId': 1111111,
        'amount': 50000,
        'resultCode': 9000
    }
    payment_repo.update_payment_result_momo(momo_update_data)
    payment = test_session.query(Payment).filter_by(code='PAY_BK1').first()
    assert payment.status == PaymentStatus.FAILED
    assert payment.booking.payment_status == BookingPaymentStatus.PENDING
#
# #update khi quá hạn
def test_update_payment_expired(test_session, sample_payments):
    expired_payment = Payment(
        code="PAY_BK999",
        booking_code="BK_PAID_1",
        amount=50000,
        status=PaymentStatus.PENDING,
        expired_time=datetime.now() - timedelta(minutes=16)
    )
    test_session.add(expired_payment)
    test_session.commit()
    momo_update_data = {
        'orderId': 'PAY_BK999',
        'extraData': 'BK_PAID_1',
        'transId': 1111111,
        'amount': 50000,
        'resultCode': 0
    }
    with pytest.raises(PaymentsError) as exc:
        payment_repo.update_payment_result_momo(momo_update_data)
    assert expired_payment.status == PaymentStatus.FAILED
    assert "Payment expired" in str(exc.value.message )

def test_update_payment_not_found(test_session):
    invalid_data = {
        'orderId': 'NON_EXISTENT',
        'extraData': 'BK_WRONG',
        'transId': '123',
        'resultCode': 0
    }
    with pytest.raises(NotFoundError):
        payment_repo.update_payment_result_momo(invalid_data)

def test_create_refund_result_momo_success(test_session, sample_bookings):
    booking_code = "BK_PAID_1"
    momo_refund_data = {
        'orderId': 'REFUND_MOMO_123',
        'amount': 50000,
        'resultCode': 0
    }

    payment_repo.create_refund_result_momo(booking_code, momo_refund_data)
    refund_record = test_session.query(Payment).filter_by(code='REFUND_MOMO_123').first()

    assert refund_record is not None
    assert refund_record.booking_code == booking_code
    assert refund_record.amount == 50000
    assert refund_record.status == PaymentStatus.SUCCESS
    assert refund_record.type == PaymentType.REFUND
    assert refund_record.payment_method == "MOMO"


def test_create_refund_result_momo_failed(test_session, sample_bookings):
    booking_code = "BK_PAID_1"
    momo_refund_data = {
        'orderId': 'REFUND_MOMO_456',
        'amount': 50000,
        'resultCode': 1001
    }
    payment_repo.create_refund_result_momo(booking_code, momo_refund_data)

    refund_record = test_session.query(Payment).filter_by(code='REFUND_MOMO_456').first()

    assert refund_record.status == PaymentStatus.FAILED
    assert refund_record.type == PaymentType.REFUND


def test_get_payment_by_booking_code_found(test_session, sample_payments):
    target_booking_code = "BK_PAID_1"
    result = payment_repo.get_payment_by_booking_code(target_booking_code)
    assert result is not None
    assert isinstance(result, Payment)
    assert result.booking_code == target_booking_code
    assert result.code == "PAY_BK1"


def test_get_payment_by_booking_code_not_found(test_session, sample_payments):
    non_existent_code = "RANDOM_CODE_999"
    result = payment_repo.get_payment_by_booking_code(non_existent_code)
    assert result is None


def test_get_payment_by_booking_code_integrity(test_session, sample_payments):
    target_code = "BK_CRITICAL"
    result = payment_repo.get_payment_by_booking_code(target_code)
    assert result.booking_code == target_code
    assert result.amount == 50000
    assert result.booking.code == target_code
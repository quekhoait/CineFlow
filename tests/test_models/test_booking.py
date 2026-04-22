import pytest
from sqlalchemy.exc import IntegrityError, DataError, StatementError
from app.models.booking import Booking, BookingStatus, BookingPaymentStatus, Payment, PaymentStatus, PaymentType

class TestBookingModels:
    def test_booking_default_values(self, test_session, test_setup_user):
        booking = Booking(
            code="BK123456",
            user_id=test_setup_user.id,
            total_price=150000.0
        )
        test_session.add(booking)
        test_session.commit()

        assert booking.status == BookingStatus.BOOKED
        assert booking.payment_status == BookingPaymentStatus.PENDING

    def test_booking_missing_total_price(self, test_session, test_setup_user):
        invalid_booking = Booking(
            code="BK654321",
            user_id=test_setup_user.id
            #thiếu total_price
        )
        test_session.add(invalid_booking)

        with pytest.raises(IntegrityError):
            test_session.commit()
        test_session.rollback()

    def test_payment_default_values(self, test_session, test_setup_user):
        #tạo Booking trước
        booking = Booking(code="BK9999", user_id=test_setup_user.id, total_price=100000)
        test_session.add(booking)
        test_session.commit()

        # tạo Payment
        payment = Payment(
            code="PAY123",
            booking_code=booking.code,
            amount=100000.0
        )
        test_session.add(payment)
        test_session.commit()

        assert payment.status == PaymentStatus.PENDING
        assert payment.type == PaymentType.PAYMENT
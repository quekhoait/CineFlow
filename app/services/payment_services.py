
from app.repository import payment_repo
from app.dto.payment_dto import PaymentResponse
def create_payment(data, booking_id) -> PaymentResponse:
    try:
        payment = payment_repo.create(data, booking_id)
        return PaymentResponse().dump(payment)
    except Exception as e:
        print(f"Database Error: {str(e)}")
        raise Exception((str(e)))
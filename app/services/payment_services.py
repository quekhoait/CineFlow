from app import PaymentStatus
from app.repository import payment_repo
from app.dto.payment_dto import PaymentResponse, PaymentReFund
from app.Momo import momo

def create_payment(data, booking_id) -> PaymentResponse:
    try:
        payment_req = momo.created_pay(booking_id=booking_id, amount=data.get('total_price'))
        payment = payment_repo.create(payment_req, booking_id)
        return PaymentResponse().dump(payment)
    except Exception as e:
        raise Exception((str(e)))

def process_refund(payment_id) -> PaymentReFund:
    payment = payment_repo.get_payment_by_id(payment_id)
    if not payment:
        raise Exception("Không tìm thấy thông tin thanh toán.")
    if payment.status != PaymentStatus.SUCCESSFUL:
        raise Exception("Chỉ hoàn tiền cho giao dịch đã thanh toán thành công.")
    if not payment.momo_trans_id:
        raise Exception("Không tìm thấy mã giao dịch MoMo (transId) để hoàn tiền.")
    try:
        p = payment_repo.update_status(payment_id, PaymentStatus.REFUNDED)
        return PaymentReFund().dump(p)
    except Exception as e:
        raise Exception((str(e)))

    # refund_res = momo.refund_payment(
    #     transaction_id=payment.transaction_id,
    #     amount=payment.amount,
    #     trans_id=payment.momo_trans_id
    # )
    # if refund_res.get('resultCode') == 0:
    #     return payment_repo.update_status(payment_id, 'REFUND')

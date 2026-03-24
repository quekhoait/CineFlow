import requests, uuid, hmac, hashlib
from config import ACCESS_KEY, SECRET_KEY, NGROCK
import time
from flask import request, jsonify
from app import db
from app.repository import payment_repo
from flask import Blueprint


# ===== MOMO SANDBOX CONFIG =====
PARTNER_CODE = "MOMO"
ACCESS_KEY = ACCESS_KEY
SECRET_KEY = SECRET_KEY
ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/create"
RETURN_URL = "https://71fa-1-52-202-58.ngrok-free.app/momo/return"
IPN_URL = "https://71fa-1-52-202-58.ngrok-free.app/api/payment/momo/ipn"
EXPIRE_AFTER= 15

def create_signature(data, secret):
    return hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()


def created_pay(booking_id, amount):
    # session["momo_user_id"] = current_user.id
    request_id = str(uuid.uuid4())
    order_id = f"{booking_id}_{int(time.time())}"
    raw_signature = (
        f"accessKey={ACCESS_KEY}"
        f"&amount={int(amount)}"
        f"&extraData="
        f"&ipnUrl={IPN_URL}"
        f"&orderId={order_id}"
        f"&orderInfo=Test MoMo Flask"
        f"&partnerCode={PARTNER_CODE}"
        f"&redirectUrl={RETURN_URL}"
        f"&requestId={request_id}"
        f"&requestType=captureWallet"
    )

    signature = create_signature(raw_signature, SECRET_KEY)

    payload = {
        "partnerCode": PARTNER_CODE,
        "accessKey": ACCESS_KEY,
        "requestId": request_id,
        "amount": amount,
        "orderId": order_id,
        "orderInfo": "Test MoMo Flask",
        "redirectUrl": RETURN_URL,
        "ipnUrl": IPN_URL,
        "extraData": "",
        "requestType": "captureWallet",
        "signature": signature,
        "expireAfter":EXPIRE_AFTER,
        "lang": "vi"
    }
    res = requests.post(ENDPOINT, json=payload).json()
    return res

def momo_ipn():
    data = request.get_json()
    transaction_id = data.get("orderId")
    result_code = data.get("resultCode")
    momo_trans_id = data.get("transId")
    payment = payment_repo.get_payment_by_trans_id(transaction_id)
    if result_code == 0:
        payment.status = 'SUCCESSFUL'
        payment.momo_trans_id = momo_trans_id
    else:
        payment.status = "FAILED"
    db.session.commit()
    return jsonify({"message": "OK"})


def refund_payment(transaction_id, amount, trans_id):
    request_id = str(uuid.uuid4())
    refund_order_id = str(uuid.uuid4())
    description = f"Refund order {transaction_id}"

    raw_signature = (
        f"accessKey={ACCESS_KEY}"
        f"&amount={int(amount)}"
        f"&description={description}"
        f"&orderId={refund_order_id}"
        f"&partnerCode={PARTNER_CODE}"
        f"&requestId={request_id}"
        f"&transId={trans_id}"
    )

    signature = create_signature(raw_signature, SECRET_KEY)

    payload = {
        "partnerCode": PARTNER_CODE,
        "requestId": request_id,
        "amount": int(amount),
        "orderId": refund_order_id,
        "transId": int(trans_id),
        "description": description,
        "signature": signature,
        "accessKey": ACCESS_KEY,
        "lang": "vi"
    }
    res = requests.post(
        "https://test-payment.momo.vn/v2/gateway/api/refund",
        json=payload
    ).json()

    print("Refund raw signature:", raw_signature)
    print("res:", res)
    return res



# def momo_return():
#     user_id = session.get("momo_user_id")
#     if not user_id:
#         return redirect(url_for("login"))
#
#     session["user_id"] = user_id  # khôi phục lại
#     return redirect(url_for("my-cart"))
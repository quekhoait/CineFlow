import requests, uuid, hmac, hashlib
from config import ACCESS_KEY, SECRET_KEY, NGROCK
import time


# ===== MOMO SANDBOX CONFIG =====
PARTNER_CODE = "MOMO"
ACCESS_KEY = ACCESS_KEY
SECRET_KEY = SECRET_KEY
ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/create"
RETURN_URL = "https://4fd6-118-68-151-247.ngrok-free.app/momo/return"
IPN_URL = "https://4fd6-118-68-151-247.ngrok-free.app/momo/ipn"
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
        "&expireAfter":EXPIRE_AFTER,
        "lang": "vi"
    }
    res = requests.post(ENDPOINT, json=payload).json()
    print(booking_id)
    return res


def TransactionStatus():
    order_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    raw_signature = (
        f"accessKey={ACCESS_KEY}"
        f"&orderId={order_id}"
        f"&partnerCode={PARTNER_CODE}"
        f"&requestId={request_id}"
    )
    signature = hmac.new(
        SECRET_KEY.encode(),
        raw_signature.encode(),
        hashlib.sha256
    ).hexdigest()

    payload = {
        "partnerCode": PARTNER_CODE,
        "accessKey": ACCESS_KEY,
        "requestId": request_id,
        "orderId": order_id,
        "signature": signature,
        "lang": "vi"
    }
    res = requests.post(
        "https://test-payment.momo.vn/v2/gateway/api/query",
        json=payload
    ).json()
    return jsonify(res)


def momo_ipn():
    data = request.json
    order_id = data.get("orderId")
    result_code = data.get("resultCode")
    trans_id = data.get("transId")
    payment = PaymentDao.get_by_momo_id(order_id)
    if not payment:
        return jsonify({"message": "payment not found"}), 404

    if result_code == 0:
        payment.status =  PaymentStatus.success
        payment.momo_trans_id = trans_id
    else:
        payment.status = "failed"

    db.session.commit()
    return jsonify({"message": "OK"})

def momo_return():
    user_id = session.get("momo_user_id")
    if not user_id:
        return redirect(url_for("login"))

    session["user_id"] = user_id  # khôi phục lại
    return redirect(url_for("my-cart"))
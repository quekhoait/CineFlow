import hashlib
import hmac
import uuid
from abc import ABC, abstractmethod
import requests

from app.dto.payment_dto import CreatePaymentResponse, MomoPaymentCallbackRequest
from app.repository import payment_repo


class PaymentStrategy(ABC):
    @abstractmethod
    def create(self, booking_code, amount):
        pass

    @abstractmethod
    def callback(self, data):
        pass

    @abstractmethod
    def refund(self, data):
        pass

class MomoPaymentStrategy(PaymentStrategy):
    def __init__(self, config):
        self.partner_code = config.get("MOMO_PARTNER_CODE")
        self.access_key = config.get("MOMO_ACCESS_KEY")
        self.secret_key = config.get("MOMO_SECRET_KEY")
        self.return_url = config.get("MOMO_RETURN_URL")
        self.ipn_url = config.get("MOMO_IPN_URL")
        self.endpoint_create = config.get("MOMO_CREATE_ENDPOINT")
        self.endpoint_refund = config.get("MOMO_REFUND_ENDPOINT")
        self.expire_after = config.get("MOMO_EXPIRE_AFTER")

    def _create_signature(self, data):
        return hmac.new(self.secret_key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()

    def create(self, booking_code, amount):
        request_id = str(uuid.uuid4())
        order_id = "HD" + uuid.uuid4().hex[:10].upper()
        order_info = "Pay with MoMo"
        request_type = "captureWallet"
        safe_amount = int(round(float(amount)))
        extract_data = booking_code

        raw_signature = (
            f"accessKey={self.access_key}&amount={safe_amount}&extraData={extract_data}"
            f"&ipnUrl={self.ipn_url}&orderId={order_id}&orderInfo={order_info}"
            f"&partnerCode={self.partner_code}&redirectUrl={self.return_url}"
            f"&requestId={request_id}&requestType={request_type}"
        )
        signature = self._create_signature(raw_signature)
        payload = {
            "partnerCode": self.partner_code,
            "accessKey": self.access_key,
            "requestId": request_id,
            "amount": safe_amount,
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": self.return_url,
            "ipnUrl": self.ipn_url,
            "extraData": extract_data,
            "requestType": request_type,
            "signature": signature,
            "expireAfter": self.expire_after,
            "lang": "vi"
        }
        res = requests.post(self.endpoint_create, json=payload).json()
        payment_repo.create_new_payment_with_momo(booking_code, res)
        return CreatePaymentResponse().load(res)

    def callback(self, data):
        data = MomoPaymentCallbackRequest().load(data)
        payment_repo.update_payment_result_momo(data)

    def refund(self, data):
        order_id = "RF"+uuid.uuid4().hex[:10].upper()
        request_id =  str(uuid.uuid4())

        raw_signature = (
            f"accessKey={self.access_key}"
            f"&amount={data['amount']}"
            f"&description={data['description']}"
            f"&orderId={order_id}"
            f"&partnerCode={self.partner_code}"
            f"&requestId={request_id}"
            f"&transId={data['transaction_id']}"
        )
        signature = self._create_signature(raw_signature)
        payload = {
            "partnerCode": self.partner_code,
            "requestId": request_id,
            "orderId": order_id,
            "amount": data['amount'],
            "transId": data['transaction_id'],
            "lang": "vi",
            "description": data['description'],
            "signature": signature
        }

        res = requests.post(self.endpoint_refund, json=payload).json()
        payment_repo.create_refund_result_momo(data['booking_code'],res)

class PaymentContext:
    def __init__(self, config):
        self.method_payment = {
            "momo": MomoPaymentStrategy(config),
        }

    def create(self, method, booking_code, amount):
        return self.method_payment.get(method).create(booking_code, amount)

    def callback(self,method, data):
        self.method_payment.get(method).callback(data)

    def refund(self,method, data):
        self.method_payment.get(method).refund(data)
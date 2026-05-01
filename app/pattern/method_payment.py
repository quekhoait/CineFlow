import hashlib
import hmac
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from marshmallow import ValidationError
import requests, json

from app.models import Payment, PaymentStatus
from app.dto.payment_dto import CreatePaymentResponse, MomoPaymentCallbackRequest
from app.repository import payment_repo
from app.utils.errors import  PaymentsError, NotFoundError, NoPaymentsMethod


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


    @abstractmethod
    def transaction(self, data):
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
        expiry_time = self.expire_after if self.expire_after else 1
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
            "expireAfter": expiry_time,
            "lang": "vi"
        }
        res = requests.post(self.endpoint_create, json=payload).json()
        payment_repo.create_new_payment_with_momo(booking_code, res)
        return CreatePaymentResponse().load(res)

    def callback(self, data):
        received_signature = data.get('signature')
        raw_signature = (
            f"accessKey={self.access_key}"
            f"&amount={data.get('amount')}"
            f"&extraData={data.get('extraData', '')}"
            f"&message={data.get('message', '')}"
            f"&orderId={data.get('orderId')}"
            f"&orderInfo={data.get('orderInfo', '')}"
            f"&orderType={data.get('orderType', '')}"
            f"&partnerCode={data.get('partnerCode')}"
            f"&payType={data.get('payType', '')}"
            f"&requestId={data.get('requestId')}"
            f"&responseTime={data.get('responseTime')}"
            f"&resultCode={data.get('resultCode')}"
            f"&transId={data.get('transId')}"
        )
        my_signature = self._create_signature(raw_signature)
        if my_signature != received_signature:
            raise PaymentsError("Chữ ký MoMo không hợp lệ!")
        try:
            validated_data = MomoPaymentCallbackRequest().load(data)
            if not isinstance(validated_data, dict):
                validated_data = vars(validated_data)
        except ValidationError as err:
            raise PaymentsError(f"Dữ liệu MoMo không hợp lệ: {err.messages}")
        order_id = validated_data.get('orderId')
        booking_code = validated_data.get('extraData')
        pay = Payment.query.filter_by(
            code=order_id,
            booking_code=booking_code
        ).first()
        if not pay:
            raise PaymentsError("Không tìm thấy đơn hàng!")
        payment_repo.update_payment_result_momo(validated_data)

    def transaction(self, data):
        order_id = data.get('orderId')
        request_id = str(uuid.uuid4())
        raw_signature = (
            f"accessKey={self.access_key}"
            f"&orderId={order_id}"
            f"&partnerCode={self.partner_code}"
            f"&requestId={request_id}"
        )
        signature = self._create_signature(raw_signature)

        payload = {
            "partnerCode": self.partner_code,
            "requestId": request_id,
            "orderId": order_id,
            "signature": signature,
            "lang": "vi"
        }

        try:
            endpoint_query = "https://test-payment.momo.vn/v2/gateway/api/query"
            response = requests.post(endpoint_query, json=payload, timeout=10)
            res_json = response.json()

            if res_json.get('resultCode') == 0:
                pay = Payment.query.filter_by(code=order_id).first()
                if pay:
                    if pay.status != PaymentStatus.SUCCESS:
                        payment_repo.update_payment_result_momo(res_json)
            return res_json

        except (PaymentsError, NotFoundError) as e:
            raise e
        except Exception as e:
            return {"resultCode": -1, "message": f"Query logic error: {str(e)}"}

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

        result_code = 0
        if data['amount'] != 0:
            res = requests.post(self.endpoint_refund, json=payload).json()

            payment_repo.create_refund_result_momo(data['booking_code'],res)
            result_code = res.get('resultCode')

        return result_code



class PaymentContext:
    def __init__(self, config):
        self.method_payment = {
            "momo": MomoPaymentStrategy(config),
        }

    def get_strategy(self, method):
        strategy = self.method_payment.get(method.lower())
        if not strategy:
            raise NoPaymentsMethod("Payment method current is not supported")
        return strategy

    def create(self, method, booking_code, amount):
        return self.method_payment.get(method).create(booking_code, amount)

    def callback(self,method, data):
        self.method_payment.get(method).callback(data)

    def transaction(self, method, data):
        return self.method_payment.get(method).transaction(data)

    def refund(self,method, data):
        return self.method_payment.get(method).refund(data)
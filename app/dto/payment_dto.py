from marshmallow import fields, EXCLUDE

from app.dto import BaseSchema

class PaymentRequest(BaseSchema):
    booking_code = fields.Str(required=True)
    method = fields.Str(required=True)



class CreatePaymentResponse(BaseSchema):
    payUrl = fields.String(required=True)

    class Meta:
        unknown = EXCLUDE

class MomoPaymentCallbackRequest(BaseSchema):
    orderId = fields.Str(required=True)
    amount = fields.Int(required=True)
    transId = fields.Int(required=True)
    resultCode = fields.Int(required=True)
    extraData = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE
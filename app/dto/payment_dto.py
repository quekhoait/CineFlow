from marshmallow import Schema, fields

class PaymentResponse(Schema):
    pay_url = fields.String()

class PaymentReFund(Schema):
    message = fields.String()





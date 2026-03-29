from marshmallow import fields

from app.models.booking import BookingStatus, PaymentStatus, BookingPaymentStatus
from app.dto import BaseSchema

class BookingRequest(BaseSchema):
    id_show = fields.Integer(required=True, error_messages={'required': 'Show ID is required'})
    code_seats = fields.List(fields.String(), required=True, error_messages={'required': 'Seat codes is required'})

class BookingSchema(BaseSchema):
    code = fields.String(required=True, error_messages={'required': 'Booking code is required'})
    user_id = fields.Integer(required=True, error_messages={'required': 'User id is required'})
    total_price = fields.Float(required=True, error_messages={'required': 'Total price is required'})

class BookingResponse(BaseSchema):
    code = fields.String()
    total_price = fields.Float()
    status = fields.Enum(enum=BookingStatus)
    payment_status = fields.Enum(enum=BookingPaymentStatus)
    start_time = fields.DateTime()
    film_title = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class CancelRequest(BaseSchema):
    code = fields.String(required=True, error_messages={"required": "Please provide code!!"})
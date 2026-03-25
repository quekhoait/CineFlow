from marshmallow import fields

from app.models.booking import BookingStatus, PaymentStatus, BookingPaymentStatus
from app.dto import BaseSchema


class BookingResponse(BaseSchema):
    code = fields.String()
    total_price = fields.Float()
    status = fields.Enum(enum=BookingStatus)
    payment_status = fields.Enum(enum=BookingPaymentStatus)
    start_time = fields.DateTime()
    film_title = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


from marshmallow import fields

from app.models.booking import BookingStatus
from app.dto import BaseSchema


class BookingResponse(BaseSchema):
    id = fields.Integer()
    total_price = fields.Float()
    status = fields.Enum(enum=BookingStatus)
    start_time = fields.DateTime()
    file_title = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


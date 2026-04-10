from marshmallow import Schema, fields
from datetime import datetime


class CinemaResponse(Schema):
    id = fields.Integer()
    name = fields.String()
    address = fields.String()

class CinemaProvince(Schema):
    province = fields.String()
    location = fields.Nested(CinemaResponse, many=True)

class ScheduleResponse(Schema):
    id = fields.Integer()
    start_time = fields.DateTime()
    is_expired = fields.Method("check_expired")
    def check_expired(self, obj):
        return obj.start_time > datetime.now()

class CinemaFilmResponse(Schema):
    title = fields.String()
    description = fields.String()
    genre = fields.String()
    poster = fields.String()
    age_limit = fields.Integer()
    duration = fields.Integer()
    schedule = fields.Nested(ScheduleResponse, many=True)

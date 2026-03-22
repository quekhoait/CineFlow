from marshmallow import Schema, fields



class CinemaResponse(Schema):
    name = fields.String()
    address = fields.String()

class CinemaProvince(Schema):
    province = fields.String()
    location = fields.Nested(CinemaResponse, many=True)

class ScheduleResponse(Schema):
    start_time = fields.DateTime()
class CinemaFilmResponse(Schema):
    title = fields.String()
    description = fields.String()
    genre = fields.String()
    poster = fields.String()
    age_limit = fields.Integer()
    duration = fields.Integer()
    schedule = fields.Nested(ScheduleResponse, many=True)
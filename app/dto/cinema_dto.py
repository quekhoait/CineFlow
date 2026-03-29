from marshmallow import Schema, fields



class CinemaResponse(Schema):
    id = fields.Integer()
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
    schedule = fields.Method("format_schedule_flat")
    def format_schedule_flat(self, obj):
        result = []
        for i, show in enumerate(obj.schedule):
            result.append(show.start_time.isoformat())
        return result
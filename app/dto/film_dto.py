from marshmallow import Schema, fields
from datetime import datetime


class FilmRequest(Schema):
    title = fields.String(required=True, error_messages={'required': 'Title is required'})
    description = fields.String(required=True, error_messages={'required': 'Description is required'})
    poster = fields.String(required=True, error_messages={'required': 'Poster is required'})
    genre = fields.String(required=True, error_messages={'required': 'Genre is required'})
    age_limit = fields.Integer(required=True, error_messages={'required': 'Age limit is required'})
    release_date = fields.Date(required=True, error_messages={'required': 'Release date is required'})
    expired_date = fields.Date(required=True, error_messages={'required': 'Expired date is required'})
    duration = fields.Integer(required=True, error_messages={'required': 'Duration is required'})

class FilmResponse(Schema):
    title = fields.String()
    description = fields.String()
    genre = fields.String()
    poster = fields.String()
    age_limit = fields.Integer()
    release_date = fields.Date()
    expired_date = fields.Date()
    duration = fields.Integer()

class FilmResponseBase(Schema):
    id = fields.Integer()
    title = fields.String()
    poster = fields.String()
    release_date = fields.Date()
    expired_date = fields.Date()

class ScheduleResponse(Schema):
    id = fields.Integer()
    start_time = fields.DateTime()
    is_expired = fields.Method("check_expired")
    def check_expired(self, obj):
        return obj.start_time > datetime.now()

class FilmCinemaResponse(Schema):
    province = fields.String()
    name = fields.String()
    address = fields.String()
    schedule = fields.Nested(ScheduleResponse, many=True)
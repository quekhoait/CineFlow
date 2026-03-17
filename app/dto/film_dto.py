from marshmallow import Schema, fields


class CreateFilm(Schema):
    title = fields.String(required=True, error_messages={'required': 'Title is required'})
    description = fields.String(required=True, error_messages={'required': 'Description is required'})
    genre = fields.String(required=True, error_messages={'required': 'Genre is required'})
    age_limit = fields.Integer(required=True, error_messages={'required': 'Age limit is required'})
    release_date = fields.Date(required=True, error_messages={'required': 'Release date is required'})
    expired_date = fields.Date(required=True, error_messages={'required': 'Expired date is required'})
    duration = fields.Integer(required=True, error_messages={'required': 'Duration is required'})

class GetFilm(Schema):
    title = fields.String()
    description = fields.String()
    genre = fields.String()
    age_limit = fields.Integer()
    release_date = fields.Date()
    expired_date = fields.Date()
    duration = fields.Integer()
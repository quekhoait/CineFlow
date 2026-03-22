from marshmallow import Schema, fields, validate, ValidationError, post_load
from types import SimpleNamespace

class BaseSchema(Schema):
    @post_load
    def make_object(self, data, **kwargs):
        return SimpleNamespace(**data)

from types import SimpleNamespace

from marshmallow import Schema, post_load


class BaseSchema(Schema):
    @post_load
    def make_object(self, data, **kwargs):
        return SimpleNamespace(**data)
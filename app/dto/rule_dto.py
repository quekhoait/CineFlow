from marshmallow import fields

from app.dto import BaseSchema

class RulesDTO(BaseSchema):
    name = fields.Str(required=True, error_messages={"required": "Please provide a valid key"})
    value = fields.Str(required=True, error_messages={"required": "Please provide a valid value"})
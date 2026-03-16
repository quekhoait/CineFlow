from types import SimpleNamespace

from marshmallow import Schema, fields, validate, ValidationError, post_load
from app.utils.validation import PasswordField, PhoneNumberField

class BaseSchema(Schema):
    @post_load
    def make_object(self, data, **kwargs):
        return SimpleNamespace(**data)

class OPTRequest(BaseSchema):
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})

class RegisterRequest(BaseSchema):
    username = fields.String(required=True, error_messages={'required': 'Username is required'})
    email = fields.Email(required=True, error_messages={'required': 'Email is required', 'invalid': 'Email is invalid'})
    password = PasswordField(required=True, error_messages={'required': 'Password is required'})
    full_name = fields.String(required=True, error_messages={'required': 'Full name is required'})
    phone_number = PhoneNumberField(required=False, load_default=None)
    otp = fields.String(required=True, error_messages={'required': 'OTP is required'})


class UserAuthMethodRequest(BaseSchema):
    user_id = fields.Integer(required=True, error_messages={'required': 'User id is required'})
    provider = fields.String(required=True, error_messages={'required': 'Provider is required'})
    provider_id = fields.Integer(required=True, error_messages={'required': 'Provider id is required'})

class EmailLoginRequest:
    email: str
    password: str

class UserResponse:
    username: str
    full_name: str
    phone_number: str
    email: str
    avatar: str
    is_active: bool

class LoginResponse:
    access_token: str
    refresh_token: str
    user: UserResponse
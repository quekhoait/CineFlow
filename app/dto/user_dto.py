from marshmallow import fields
from app.dto import BaseSchema
from app.utils.validation import PasswordField, PhoneNumberField

class OPTRequest(BaseSchema):
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})

class RegisterRequest(BaseSchema):
    username = fields.String(required=True, error_messages={'required': 'Username is required'})
    email = fields.Email(required=True, error_messages={'required': 'Email is required', 'invalid': 'Email is invalid'})
    password = PasswordField(required=True, error_messages={'required': 'Password is required'})
    full_name = fields.String(required=True, error_messages={'required': 'Full name is required'})
    phone_number = PhoneNumberField(required=False, load_default=None)
    avatar = fields.String(required=False, load_default=None)
    otp = fields.String(required=True, error_messages={'required': 'OTP is required'})

class GoogleAuthRequest(BaseSchema):
    username = fields.String(required=True, error_messages={'required': 'Username is required'})
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    full_name = fields.String(required=True, error_messages={'required': 'Full name is required'})
    provider = fields.String(required=True, error_messages={'required': 'Provider is required'})
    provider_id = fields.String(required=True, error_messages={'required': 'Provider id is required'})
    avatar = fields.String(required=False, load_default=None)

class UserAuthMethodRequest(BaseSchema):
    user_id = fields.Integer(required=True, error_messages={'required': 'User id is required'})
    provider = fields.String(required=True, error_messages={'required': 'Provider is required'})
    provider_id = fields.Integer(required=True, error_messages={'required': 'Provider id is required'})

class EmailLoginRequest(BaseSchema):
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    password = PasswordField(required=True, error_messages={'required': 'Password is required'})

class UserResponse(BaseSchema):
    id = fields.Integer()
    username = fields.String()
    full_name = fields.String()
    phone_number = PhoneNumberField(required=False, load_default=None)
    avatar = fields.String(required=False, load_default=None)
    email = fields.Email()
    is_active = fields.Boolean()

class UserLoginResponse(BaseSchema):
    access_token = fields.String()
    refresh_token = fields.String()
    user = fields.Nested(UserResponse)

class OAuth2Response(BaseSchema):
    url = fields.String(required=False)

class TokenResponse(BaseSchema):
    access_token = fields.String()
from marshmallow import fields, EXCLUDE, pre_load, validate
from wtforms.validators import readonly

from app.dto import BaseSchema
from app.utils.validation import PasswordField, PhoneNumberField, CloudinaryImageField


class OPTRequest(BaseSchema):
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})

class RegisterRequest(BaseSchema):
    username = fields.String(required=True, error_messages={'required': 'Username is required'}, validate=validate.Length(min=1, error='Username is required'))
    email = fields.Email(required=True, error_messages={'required': 'Email is required', 'invalid': 'Email is invalid'}, validate=validate.Length(min=1, error='Email is required'))
    password = PasswordField(required=True, error_messages={'required': 'Password is required'}, validate=validate.Length(min=1, error='Password is required'))
    full_name = fields.String(required=True, error_messages={'required': 'Full name is required'}, validate=validate.Length(min=1, error='Fullname is required'))
    phone_number = PhoneNumberField(required=False, load_default=None, validate=validate.Length(min=1, error='Password is required'))
    avatar = fields.String(required=False, load_default=None)
    otp = fields.String(required=True, error_messages={'required': 'OTP is required'}, validate=validate.Length(min=1, error='Username is required'))

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def strip_whitespace(self, data, **kwargs):
        fields_to_exclude = ['password']

        for key, value in data.items():
            if key not in fields_to_exclude and isinstance(value, str):
                data[key] = value.strip()
        return data

class GoogleAuthRequest(BaseSchema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    full_name = fields.String(required=True)
    provider = fields.String(required=True)
    provider_id = fields.String(required=True)
    avatar = fields.String(allow_none=True)

    @pre_load
    def map_google_data(self, data, **kwargs):
        return {
            "username": data.get("given_name"),
            "full_name": data.get("name"),
            "email": data.get("email"),
            "provider": "GOOGLE",
            "provider_id": data.get("sub"),
            "avatar": data.get("picture")
        }

class UserAuthMethodRequest(BaseSchema):
    user_id = fields.Integer(required=True)
    provider = fields.String(required=True)
    provider_id = fields.Integer(required=True)

class EmailLoginRequest(BaseSchema):
    email = fields.Email(required=True, error_messages={'required': 'Email is required'}, validate=validate.Length(min=1, error='Username is required'))
    password = PasswordField(required=True, error_messages={'required': 'Password is required'}, validate=validate.Length(min=1, error='Username is required'))

class UserUpdateRequest(BaseSchema):
    username = fields.Str(validate=validate.Length(min=1, error='Username is required'), required=True, error_messages={'required': 'Username is required'})
    full_name = fields.Str(validate=validate.Length(min=1, error='Username is required'), required=True, error_messages={'required': 'Fullname is required'})
    phone_number = PhoneNumberField(required=True)
    avatar = CloudinaryImageField(folder='avatars')
    class Meta:
        unknown = EXCLUDE

class UserResponse(BaseSchema):
    id = fields.Integer()
    username = fields.String()
    full_name = fields.String()
    phone_number = fields.String()
    avatar = fields.String()
    email = fields.String()
    is_active = fields.Boolean()

class OAuth2Response(BaseSchema):
    url = fields.String(required=False)

class TokenResponse(BaseSchema):
    access_token = fields.String()
    refresh_token = fields.String()
from marshmallow import fields, EXCLUDE, pre_load
from wtforms.validators import readonly

from app.dto import BaseSchema
from app.utils.validation import PasswordField, PhoneNumberField, CloudinaryImageField


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

    class Meta:
        unknown = EXCLUDE

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
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    password = fields.String(required=True, error_messages={'required': 'Password is required'})

class UserUpdateRequest(BaseSchema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str()
    full_name = fields.Str()
    phone_number = PhoneNumberField()
    avatar = CloudinaryImageField(folder='avatars', allow_none=True, required=False)

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
    refresh_token = fields.String()
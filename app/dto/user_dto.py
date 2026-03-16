from marshmallow import Schema, fields, validate, ValidationError

from app.utils.validation import PasswordField, PhoneNumberField

class OPTRequest(Schema):
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})

class RegisterRequest(Schema):
    username = fields.String(required=True, error_messages={'required': 'Username is required'})
    email = fields.Email(required=True, error_messages={'required': 'Email is required', 'invalid': 'Email is invalid'})
    password = PasswordField(required=True, error_messages={'required': 'Password is required'})
    full_name = fields.String(required=True, error_messages={'required': 'Full name is required'})
    phone_number = PhoneNumberField(required=True, error_messages={'required': 'Phone number is required'})

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
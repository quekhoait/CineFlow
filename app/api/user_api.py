from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.dto.user_dto import RegisterRequest, OPTRequest
from app.services import user_service as user_service
from flask import Blueprint, request

from app.utils.errors import InvalidOtpError, ExistingEmailError, RegisterFailed
from app.utils.json import NewPackage

user_api = Blueprint('user', __name__, url_prefix='/user')

@user_api.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        data = OPTRequest().load(data)
        user_service.send_otp(data)
        return NewPackage(success=True, message="OTP sent successfully", status_code=200)
    except ValidationError as e:
        return NewPackage(success=False, message="Invalid Input", data=e.messages, status_code=400)
    except ExistingEmailError as e:
        return NewPackage(success=False, message=e.message, status_code=e.status_code)
    except Exception as e:
        print(e)
        return NewPackage(success=False, message="Internal Server Error", status_code=500)


@user_api.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        data = RegisterRequest().load(data)
        user_service.register(data)
        return NewPackage(success=True, message="Registered successfully", status_code=201)
    except ValidationError as e:
        return NewPackage(success=False, message="Invalid Input", data=e.messages, status_code=400)
    except (InvalidOtpError, ExistingEmailError) as e:
        return NewPackage(success=False, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(success=False, message="Register failed", status_code=500)

@user_api.route('/auth/<provider>', methods=['POST', 'GET'])
def authenticate(provider):
    pass


@user_api.route('/auth/<provider>/callback', methods=['POST'])
def callback(provider):
    pass

@user_api.route('/auth/refresh', methods=['POST'])
def refresh():
    pass

@user_api.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    pass





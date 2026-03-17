from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.dto.user_dto import RegisterRequest, OPTRequest
from app.services import user_service as user_service
from flask import Blueprint, request

from app.utils.errors import InvalidOtpError, ExistingUserError, UserLoginFailed, UnauthorizedError
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
    except ExistingUserError as e:
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
    except (InvalidOtpError, ExistingUserError) as e:
        return NewPackage(success=False, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(success=False, message="Register failed", status_code=500)

@user_api.route('/auth/<provider>', methods=['POST', 'GET'])
def authenticate(provider):
    try:
        data = request.get_json() if request.method == 'POST' else {}
        response = user_service.authenticate(provider=provider, data=data)
        return NewPackage(
            success=True,
            message=f"Login with {provider} successfully" if provider == 'email'
                    else f"Get link {provider} successfully",
            data=response,
            status_code=200
            )
    except UserLoginFailed as e:
        return NewPackage(success=False, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(success=False, message="Have a problem in login flow", status_code=500)


@user_api.route('/auth/<provider>/callback', methods=['GET'])
def callback(provider):
    try:
        response = user_service.callback(provider=provider, request=request)
        return NewPackage(success=True, message=f"Login {provider} successfully", status_code=200, data=response)
    except Exception as e:
        return NewPackage(success=False, message="Have a problem in login flow", status_code=500)

@user_api.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        response = user_service.refresh()
        return NewPackage(success=True, message="Refresh successfully", status_code=200, data=response)
    except Exception as e:
        return NewPackage(success=False, message="Refresh failed", status_code=500)

@user_api.route('/profile', methods=['GET'])
# @jwt_required()
def profile():
    try:
        response = user_service.profile()
        return NewPackage(success=True, message="Get profile successfully", status_code=200, data=response)
    except UnauthorizedError as e:
        return NewPackage(success=False, message=e.message, status_code=e.status_code)
    except Exception as e:
        print(e)
        return NewPackage(success=False, message="Have a problem while load profile", status_code=500)

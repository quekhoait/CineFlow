from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.dto.user_dto import RegisterRequest, OPTRequest
from app.services import user_service as user_service
from flask import Blueprint, request

from app.utils.errors import InvalidOtpError, ExistingUserError, UserLoginFailed, UnauthorizedError
from app.utils.json import NewPackage, StatusResponse

user_api = Blueprint('user', __name__, url_prefix='/user')

@user_api.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        data = OPTRequest().load(data)
        user_service.send_otp(data)
        return NewPackage(status=StatusResponse.SUCCESS, message="OTP sent successfully", status_code=200)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid Input", data=e.messages, status_code=400)
    except ExistingUserError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", status_code=500)


@user_api.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        data = RegisterRequest().load(data)
        user_service.register(data)
        return NewPackage(status=StatusResponse.SUCCESS, message="Registered successfully", status_code=201)

    except (InvalidOtpError, ExistingUserError) as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Register failed", status_code=500)

@user_api.route('/auth/<provider>', methods=['POST', 'GET'])
def authenticate(provider):
    try:
        data = request.get_json() if request.method == 'POST' else {}
        response = user_service.authenticate(provider=provider, data=data)
        return  NewPackage(
                    status=StatusResponse.SUCCESS,
                    message=f"{'Login with' if provider == 'email' else 'Get link'} {provider} successfully",
                    data=response,
                    status_code=200
                )
    except UserLoginFailed as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid Input", data=e.messages, status_code=400)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem in login flow", status_code=500)


@user_api.route('/auth/<provider>/callback', methods=['GET'])
def callback(provider):
    try:
        response = user_service.callback(provider=provider, request=request)
        return NewPackage(status=StatusResponse.SUCCESS, message=f"Login {provider} successfully", status_code=200, data=response)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem in login flow", status_code=500)

@user_api.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        response = user_service.refresh()
        return NewPackage(status=StatusResponse.SUCCESS, message="Refresh successfully", status_code=200, data=response)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Refresh failed", status_code=500)

@user_api.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        response = user_service.profile()
        return NewPackage(status=StatusResponse.SUCCESS, message="Get profile successfully", status_code=200, data=response)
    except UnauthorizedError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        print(e)
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem while load profile", status_code=500)

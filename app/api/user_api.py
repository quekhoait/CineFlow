import logging

from flask_jwt_extended import jwt_required, unset_jwt_cookies
from marshmallow import ValidationError
from app.dto.user_dto import RegisterRequest, OPTRequest, TokenResponse, UserUpdateRequest, EmailLoginRequest
from app.services import user_service as user_service
from flask import Blueprint, request, render_template

from app.utils.errors import InvalidOtpError, ExistingUserError, UserLoginEmailFailed, UnauthorizedError, APIError
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
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        logging.error(f"Send otp error: {e}")
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", status_code=500)


@user_api.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        data = RegisterRequest().load(data)
        user_service.register(data)
        return NewPackage(status=StatusResponse.SUCCESS, message="Registered successfully", status_code=201)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid Input", data=e.messages, status_code=400)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        logging.error(f"Register error: {e}")
        return NewPackage(status=StatusResponse.ERROR, message="Register failed", status_code=500)

@user_api.route('/auth/<provider>', methods=['POST', 'GET'])
def authenticate(provider):
    try:
        data = EmailLoginRequest().load(request.get_json()) if request.method == 'POST' else {}
        response = user_service.authenticate(provider=provider, data=data)
        return  NewPackage(
                    status=StatusResponse.SUCCESS,
                    message=f"{'Login with' if provider == 'email' else 'Get link'} {provider} successfully",
                    data=response,
                    status_code=200
                )
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid data input", data=e.messages, status_code=400)
    except Exception as e:
        logging.error(f"Authenticate {provider} error: {e}")
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem in login flow", status_code=500)


@user_api.route('/auth/<provider>/callback', methods=['GET'])
def callback(provider):
    try:
        response = user_service.callback(provider=provider, request=request)
        return NewPackage(
            status=StatusResponse.SUCCESS,
            message=f"{'Login with' if provider == 'email' else 'Get link'} {provider} successfully",
            data=response,
            status_code=200
        )
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        logging.error(f"Callback {provider} error: {e}")
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem in login flow", status_code=500)


@user_api.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        response = user_service.refresh()
        return NewPackage(status=StatusResponse.SUCCESS, message="Refresh successfully", status_code=200, data=response)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        logging.error(f"Refresh error: {e}")
        return NewPackage(status=StatusResponse.ERROR, message="Refresh failed", status_code=500)

@user_api.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    try:
        if request.method == 'GET':
            response = user_service.profile()
        else:
            data = {**request.form.to_dict(), **request.files.to_dict()}
            data = UserUpdateRequest().load(data)
            print(data)
            response = user_service.update(data)
        return NewPackage(status=StatusResponse.SUCCESS, message="Get profile successfully", status_code=200, data=response)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid data input", data=e.messages, status_code=400)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        print(e)
        logging.error(f"{request.method} profile error: {e}")
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem while load profile", status_code=500)

@user_api.route('/auth/me', methods=['GET'])
@jwt_required()
def me():
    return NewPackage(status=StatusResponse.SUCCESS, message="You is in system", status_code=200)

@user_api.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    resp = NewPackage(status=StatusResponse.SUCCESS, message="Logout successfully", status_code=200)
    unset_jwt_cookies(resp)
    return resp
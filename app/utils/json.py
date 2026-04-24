from flask import jsonify, make_response, redirect
from enum import Enum

from flask_jwt_extended import set_access_cookies, set_refresh_cookies

class StatusResponse(Enum):
    SUCCESS = "success",
    ERROR = "error",
    PENDING = "pending",

def NewPackage(status: StatusResponse, message: str, data=None, status_code=200):
    serialized_data = None
    access_token = None
    refresh_token = None

    if data is not None:
        if hasattr(data, 'to_dict'):
            serialized_data = data.to_dict()
        elif isinstance(data, dict):
            serialized_data = data.copy()
        else:
            serialized_data = data

    is_dict_data = isinstance(serialized_data, dict)
    if is_dict_data:
        access_token = serialized_data.pop("access_token", None)
        refresh_token = serialized_data.pop("refresh_token", None)

    body = {
        'status': status.value[0] if hasattr(status, 'value') else status,
        'message': message,
    }

    if serialized_data is not None and serialized_data != {}:
        body['data'] = serialized_data

    if is_dict_data and 'redirect' in serialized_data:
        redirect_url = serialized_data['redirect']
        final_code = status_code if str(status_code).startswith('3') else 302
        resp = make_response(redirect(redirect_url), final_code)
    else:
        resp = make_response(jsonify(body), status_code)

    if access_token:
        set_access_cookies(resp, access_token)
    if refresh_token:
        set_refresh_cookies(resp, refresh_token)

    return resp

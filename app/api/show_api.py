from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.api.user_api import profile
from app.services import show_service
from app.utils.errors import NotFoundError, APIError
from app.utils.json import NewPackage, StatusResponse

show_api = Blueprint('show', __name__, url_prefix='/shows')

@show_api.route('/')
def shows():
    pass

@show_api.route('/<int:show_id>', methods=['GET'])
@jwt_required()
def get_show_seats(show_id):
    try:
        response = show_service.get_show_seats_info(show_id)
        return NewPackage(status=StatusResponse.SUCCESS, message="Get show seats successfully", data=response, status_code=200)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem while getting show seats info", status_code=500)
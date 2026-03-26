from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.dto.booking_dto import CancelRequest
from app.services import booking_service
from app.utils.json import NewPackage, StatusResponse
from app.utils.errors import *

booking_api = Blueprint('booking', __name__, url_prefix='/bookings')

@booking_api.route('/')
def bookings():
    pass

@booking_api.route('/create')
def create():
    pass

@booking_api.route('/bookings/<int:id>')
def booking(id):
    pass

@booking_api.route('/cancel', methods = ['POST'])
@jwt_required()
def cancel():
    try:
        booking_service.cancel(CancelRequest().load(request.get_json()).code)
        return NewPackage(status=StatusResponse.SUCCESS, message="Cancel ticket success! You wait refuse money", status_code=200)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        print(str(e))
        return NewPackage(status=StatusResponse.ERROR, message="Cancel ticket failed", status_code=500)
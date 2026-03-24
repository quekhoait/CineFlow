from flask import Blueprint
from flask_jwt_extended import jwt_required

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

@booking_api.route('/<int:booking_id>/cancel', methods = ['POST'])
@jwt_required()
def cancel(booking_id):
    try:
        booking_service.cancel(booking_id)
        return NewPackage(status=StatusResponse.SUCCESS, message="Cancel ticket success! You wait refuse money", status_code=200)
    except (NotFoundError, ExpiredError) as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        print(str(e))
        return NewPackage(status=StatusResponse.ERROR, message="Cancel ticket failed", status_code=500)
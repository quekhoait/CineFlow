import logging

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.dto.booking_dto import BookingRequest, CancelRequest
from app.services import booking_service
from app.utils.json import NewPackage, StatusResponse
from app.utils.errors import *

booking_api = Blueprint('booking', __name__, url_prefix='/bookings')

@booking_api.route('', methods=['GET'])
@jwt_required()
def bookings():
    try:
        response = booking_service.get_bookings()
        return NewPackage(status=StatusResponse.SUCCESS, message='Get booking list successfully' , data=response, status_code=200)
    except Exception as e:
        logging.error("Get list bookings error" + str(e))
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem while getting booking list", status_code=500)

@booking_api.route('/create', methods=['POST'])
@jwt_required()
def create():
    try:
        data = request.get_json()
        data = BookingRequest().load(data)
        response = booking_service.create(data)
        return NewPackage(status=StatusResponse.SUCCESS, message="Booking created successfully", data=response, status_code=201)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid data", status_code=400, data=e.messages)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        logging.error("Create booking error" + str(e))
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem in login flow" + str(e), status_code=500)


@booking_api.route('/<string:code>', methods=['GET'])
@jwt_required()
def booking(code):
    try:
        response = booking_service.get_booking_by_code(code)
        return NewPackage(status=StatusResponse.SUCCESS, message="Get booking successfully", data=response, status_code=200)
    except NotFoundError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        print(e)
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem while getting booking detail", status_code=500)

@booking_api.route('/<string:code>/cancel', methods=['POST'])
@jwt_required()
def cancel(code):
    try:
        booking_service.cancel(code, request.get_json()['method'])
        return NewPackage(status=StatusResponse.SUCCESS, message="Cancel ticket success! You wait refuse money", status_code=200)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        logging.error("Cancel ticket error" + str(e))
        return NewPackage(status=StatusResponse.ERROR, message="Cancel booking failed", status_code=500)
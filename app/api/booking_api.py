from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.services import booking_service
from app.utils.json import NewPackage, StatusResponse

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

@booking_api.route('/<int:id>/cancel', methods = ['POST'])
@jwt_required()
def cancel(id):
    try:
        response = booking_service.cancel(id)
    except Exception as e:
        pass
from flask import Blueprint

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

@booking_api.route('/<int: id>/cancel', methods = ['POST'])
def cancel():
    # id_booking -> CANCEL ->
    pass
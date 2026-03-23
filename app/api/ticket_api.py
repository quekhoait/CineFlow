from flask import Blueprint

ticket_api = Blueprint('ticket', __name__, url_prefix='/tickets')

@ticket_api.route('/booking')
def booking():
    pass

@ticket_api.route('/bookings/')
def bookings():
    pass

@ticket_api.route('/bookings/<int:id>/')
def booking(id):
    pass

@ticket_api.route('/cancel')
def cancel():
    pass
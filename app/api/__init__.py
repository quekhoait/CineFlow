import logging

from flask import Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

from .user_api import user_api
from .booking_api import booking_api
from .show_api import  show_api
from .film_api import film_api
from .payment_api import payment_api
from .cinema_api import cinema_api
from .rules_api import rules_api

api.register_blueprint(user_api)
api.register_blueprint(booking_api)
api.register_blueprint(show_api)
api.register_blueprint(film_api)
api.register_blueprint(payment_api)
api.register_blueprint(cinema_api)
api.register_blueprint(rules_api)

@api.before_request
def update_status_booking():
    try:
        from app.services import booking_service
        booking_service.update_status_booking()
    except Exception as e:
        logging.error("Update global: ", str(e))

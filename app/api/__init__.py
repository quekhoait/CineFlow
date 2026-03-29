from flask import Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

from .user_api import user_api
from .booking_api import booking_api
from .show_api import  show_api
from .film_api import film_api
from .payment_api import payment_api
api.register_blueprint(user_api)
api.register_blueprint(booking_api)
api.register_blueprint(show_api)
api.register_blueprint(film_api)
api.register_blueprint(payment_api)


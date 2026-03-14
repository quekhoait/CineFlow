from flask import Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

from .booking import booking_api
api.register_blueprint(booking_api)
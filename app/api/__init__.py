from flask import Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

from .payment_api import payment_api
api.register_blueprint(payment_api)
from flask import Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

from .user_api import user_api
from .film_api import film_api
from .cinema_api import cinema_api

api.register_blueprint(user_api)
api.register_blueprint(film_api)
api.register_blueprint(cinema_api)

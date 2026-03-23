from flask import Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

from .user_api import user_api
from .ticket_api import ticket_api
from .show_api import  show_api
from .film_api import film_api
api.register_blueprint(user_api)
api.register_blueprint(ticket_api)
api.register_blueprint(show_api)
api.register_blueprint(film_api)


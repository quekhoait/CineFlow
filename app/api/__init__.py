from flask import Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

from .user import user_api
api.register_blueprint(user_api)

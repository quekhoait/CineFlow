from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from google.oauth2.reauth import refresh_grant

from app.pattern.provider import AuthProvider

user_api = Blueprint('user', __name__, url_prefix='/user')

@user_api.route('/auth/<provider>', methods=['POST', 'GET'])
def authenticate(provider):
    data = request.get_json() or {}
    user_id = None
    try:
        auth_handler = AuthProvider.get_provider(provider.lower())
        user_id = auth_handler.authenticate(data)
    except Exception as e:
        pass

    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)








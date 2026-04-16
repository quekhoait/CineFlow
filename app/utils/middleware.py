from functools import wraps

from flask import request, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.utils.json import NewPackage


def jwt_middleware():
    from app import jwt
    from app.repository import user_repo
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        user = user_repo.get_user_by_user_id(int(identity))
        return user

def role_request(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims["role"]

            if user_role.upper() != role.upper():
                return NewPackage('error', 'You are not allowed to access this resource', status_code=403)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if 'access_token_cookie' not in request.cookies:
            return redirect(url_for('frontend.index'))
        return func(*args, **kwargs)
    return decorator

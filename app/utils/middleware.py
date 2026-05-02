import logging
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

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return NewPackage('error', 'You missing token to authenticate', status_code=401)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return NewPackage('error', 'You have expired', status_code=401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return NewPackage('error', 'Invalid token', status_code=401)

def role_request(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims["roles"]

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

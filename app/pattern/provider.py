from abc import ABC, abstractmethod
from typing import Any
from flask import url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash

from app import oauth
from app.dto.user_dto import EmailLoginRequest, UserLoginResponse, UserResponse, OAuth2Response, GoogleAuthRequest, \
    UserAuthMethodRequest
from app.repository import user_repo
from app.utils.errors import UserLoginFailed

class AuthProvider(ABC):
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, provider: str, **kwargs):
        super().__init_subclass__()
        if provider and provider not in cls._registry:
            cls._registry[provider.lower()] = cls

    @classmethod
    def get_provider(cls, provider: str):
        provider_cls = cls._registry.get(provider.lower())
        if not provider_cls:
            raise ValueError(f'Provider {provider} is not supported')
        return provider_cls()

    @abstractmethod
    def authenticate(self, data:Any) -> Any:
        pass

class EmailProvider(AuthProvider, provider='email'):
    def authenticate(self, data) -> UserLoginResponse:
        data = EmailLoginRequest().load(data)
        user = user_repo.get_user_by_email(data.email)
        if not user:
            raise UserLoginFailed()

        if not check_password_hash(user.password, data.password):
            raise UserLoginFailed()

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        user_repo.update_user_auth_method(user.id, refresh_token)

        raw_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": UserResponse().dump(user)
        }

        return UserLoginResponse().dump(raw_data)

class OtherProvider(AuthProvider, provider='other'):
    @abstractmethod
    def callback(self, data: Any):
        pass

class GoogleProvider(OtherProvider, provider='google'):
    def authenticate(self, data: dict):
        redirect_uri = url_for('api.user.callback', provider='google', _external=True)
        redirect_response = oauth.google.authorize_redirect(redirect_uri)
        target_url = redirect_response.headers['Location']
        raw_data = {
            "url": target_url
        }
        return OAuth2Response().dump(raw_data)

    def callback(self, request):
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        if not user_info:
            resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
            user_info = resp.json()

        gg_auth = GoogleAuthRequest()
        gg_auth.provider_id = user_info['sub']
        gg_auth.provider = "GOOGLE"
        gg_auth.full_name = user_info['name']
        gg_auth.email = user_info['email']
        gg_auth.username = user_info['name']
        gg_auth.avatar = user_info['picture']

        user = user_repo.get_user_by_email(gg_auth.email)
        user_id = user.id if user else None
        if not user_id:
            user = user_repo.create_user_google(gg_auth)
            user_id = user.id

        if not user_repo.get_user_id_by_provider_id(gg_auth.provider_id):
            auth_method = UserAuthMethodRequest()
            auth_method.user_id = user_id
            auth_method.provider = gg_auth.provider
            auth_method.provider_id = gg_auth.provider_id
            user_repo.create_user_auth_method(auth_method)

        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))
        user_repo.update_user_auth_method(user_id, refresh_token)

        raw_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        return raw_data

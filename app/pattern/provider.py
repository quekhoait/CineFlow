from abc import ABC, abstractmethod
from typing import Any

from cryptography.hazmat.primitives.hashes import SHA512
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from app.dto.user_dto import EmailLoginRequest, UserLoginResponse, UserResponse
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

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

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
        pass

    def callback(self, data: dict):
        pass
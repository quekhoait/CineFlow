from abc import ABC, abstractmethod

from flask_jwt_extended import create_access_token, create_refresh_token
from app.dto.user_dto import EmailLoginRequest, LoginResponse, UserResponse
from app.utils.errors import UserLoginFailed
from werkzeug.security import generate_password_hash


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

    @abstractmethod
    def authenticate(self, data: dict) -> dict:
        pass

class EmailProvider(AuthProvider, provider='email'):
    def authenticate(self, data: dict) -> LoginResponse:
        data = EmailLoginRequest(**data)
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            raise UserLoginFailed()

        if user.password != generate_password_hash(data.password):
            raise UserLoginFailed()

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        response = LoginResponse(access_token=access_token, refresh_token=refresh_token, user=UserResponse(**user))
        return response

class GoogleProvider(AuthProvider, provider='google'):
    def authenticate(self, data: dict) -> dict:
        pass
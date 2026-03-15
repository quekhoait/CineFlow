from abc import ABC, abstractmethod

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
    def authenticate(self, data: dict) -> dict:
        pass

class GoogleProvider(AuthProvider, provider='google'):
    def authenticate(self, data: dict) -> dict:
        pass
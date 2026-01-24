"""Authentication Service Interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class RegisterInput:
    """Input data for user registration."""
    email: str
    password: str
    full_name: str


@dataclass
class LoginInput:
    """Input data for user login."""
    email: str
    password: str


@dataclass
class UserOutput:
    """Output data for user."""
    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


@dataclass
class AuthTokenOutput:
    """Output data for authentication token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class IAuthService(ABC):
    """Interface for Authentication Service."""

    @abstractmethod
    async def register(self, input_data: RegisterInput) -> UserOutput:
        """Register a new user."""
        pass

    @abstractmethod
    async def login(self, input_data: LoginInput) -> AuthTokenOutput:
        """Authenticate a user and return a token."""
        pass

    @abstractmethod
    async def get_current_user(self, token: str) -> UserOutput:
        """Get the currently authenticated user from token."""
        pass

    @abstractmethod
    async def validate_token(self, token: str) -> bool:
        """Validate if a token is valid."""
        pass

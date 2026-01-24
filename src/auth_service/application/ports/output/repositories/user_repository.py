"""User Repository Interface."""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from auth_service.domain.entities.user import User


class IUserRepository(ABC):
    """Interface for User Repository."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a user."""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Find user by ID."""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update a user."""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        pass

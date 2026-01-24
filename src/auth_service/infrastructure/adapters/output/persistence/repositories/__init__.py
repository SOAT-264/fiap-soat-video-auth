"""Repositories."""
from auth_service.infrastructure.adapters.output.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

__all__ = ["SQLAlchemyUserRepository"]

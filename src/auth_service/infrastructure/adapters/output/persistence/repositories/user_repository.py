"""SQLAlchemy User Repository."""
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.domain.entities.user import User
from auth_service.application.ports.output.repositories.user_repository import IUserRepository
from auth_service.infrastructure.adapters.output.persistence.models import UserModel

from video_processor_shared.domain.value_objects import Email, Password


class SQLAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of User Repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> User:
        """Save a user."""
        model = UserModel(
            id=user.id,
            email=user.email.value,
            password_hash=user.password.hashed_value,
            password_salt=user.password.salt,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=self._to_db_datetime(user.created_at),
            updated_at=self._to_db_datetime(user.updated_at),
        )
        self._session.add(model)
        await self._session.flush()
        return user

    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Find user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        """Update a user."""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.email = user.email.value
            model.password_hash = user.password.hashed_value
            model.password_salt = user.password.salt
            model.full_name = user.full_name
            model.is_active = user.is_active
            model.updated_at = self._to_db_datetime(user.updated_at)
            await self._session.flush()
        return user

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    def _to_entity(self, model: UserModel) -> User:
        """Convert model to entity."""
        return User(
            id=model.id,
            email=Email(model.email),
            password=Password.from_hash(model.password_hash, model.password_salt),
            full_name=model.full_name,
            is_active=model.is_active,
            created_at=self._to_domain_datetime(model.created_at),
            updated_at=self._to_domain_datetime(model.updated_at),
        )

    @staticmethod
    def _to_db_datetime(value: datetime) -> datetime:
        """Convert datetime to UTC naive for TIMESTAMP WITHOUT TIME ZONE columns."""
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)

    @staticmethod
    def _to_domain_datetime(value: datetime) -> datetime:
        """Convert datetime from DB to UTC aware in domain."""
        if value.tzinfo is not None:
            return value.astimezone(UTC)
        return value.replace(tzinfo=UTC)

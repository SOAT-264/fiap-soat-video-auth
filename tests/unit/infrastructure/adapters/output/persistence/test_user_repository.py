from datetime import datetime, UTC
from types import SimpleNamespace
from uuid import uuid4

import pytest

from auth_service.domain.entities.user import User
from auth_service.infrastructure.adapters.output.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from video_processor_shared.domain.value_objects import Email, Password


class FakeResult:
    def __init__(self, model):
        self._model = model

    def scalar_one_or_none(self):
        return self._model


class FakeSession:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.flushed = 0
        self.model_to_return = None

    def add(self, model):
        self.added.append(model)

    async def flush(self):
        self.flushed += 1

    async def execute(self, stmt):
        return FakeResult(self.model_to_return)

    async def delete(self, model):
        self.deleted.append(model)


def build_user() -> User:
    return User(
        id=uuid4(),
        email=Email("john@example.com"),
        password=Password.create("StrongPass123!"),
        full_name="John Doe",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def build_model(user: User):
    return SimpleNamespace(
        id=user.id,
        email=user.email.value,
        password_hash=user.password.hashed_value,
        password_salt=user.password.salt,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@pytest.mark.asyncio
async def test_save_returns_same_user_and_flushes():
    session = FakeSession()
    repository = SQLAlchemyUserRepository(session)
    user = build_user()

    saved = await repository.save(user)

    assert saved is user
    assert len(session.added) == 1
    assert session.flushed == 1


@pytest.mark.asyncio
async def test_find_by_id_and_email_return_entity_or_none():
    session = FakeSession()
    repository = SQLAlchemyUserRepository(session)
    user = build_user()
    session.model_to_return = build_model(user)

    found_by_id = await repository.find_by_id(user.id)
    found_by_email = await repository.find_by_email(user.email.value)

    assert found_by_id is not None
    assert found_by_id.id == user.id
    assert found_by_email is not None
    assert found_by_email.email.value == user.email.value

    session.model_to_return = None
    assert await repository.find_by_id(uuid4()) is None
    assert await repository.find_by_email("none@example.com") is None


@pytest.mark.asyncio
async def test_update_updates_existing_model_or_noop_when_missing():
    session = FakeSession()
    repository = SQLAlchemyUserRepository(session)
    user = build_user()
    model = build_model(user)
    session.model_to_return = model

    user.update_name("Updated Name")
    updated = await repository.update(user)

    assert updated is user
    assert model.full_name == "Updated Name"
    assert session.flushed == 1

    session.model_to_return = None
    session.flushed = 0
    await repository.update(user)
    assert session.flushed == 0


@pytest.mark.asyncio
async def test_delete_returns_true_when_found_otherwise_false():
    session = FakeSession()
    repository = SQLAlchemyUserRepository(session)
    user = build_user()
    session.model_to_return = build_model(user)

    assert await repository.delete(user.id) is True
    assert len(session.deleted) == 1
    assert session.flushed == 1

    session.model_to_return = None
    session.flushed = 0
    assert await repository.delete(uuid4()) is False
    assert session.flushed == 0


def test_to_entity_maps_fields_correctly():
    session = FakeSession()
    repository = SQLAlchemyUserRepository(session)
    user = build_user()
    model = build_model(user)

    entity = repository._to_entity(model)
    assert entity.id == user.id
    assert entity.email.value == user.email.value
    assert entity.full_name == user.full_name

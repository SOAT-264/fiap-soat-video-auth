from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from auth_service.application.ports.input.auth_service import UserOutput
from auth_service.infrastructure.adapters.input.api import dependencies
from auth_service.infrastructure.config import Settings
from video_processor_shared.domain.exceptions import InvalidCredentialsError, UserInactiveError


@pytest.mark.asyncio
async def test_get_user_repository_returns_sqlalchemy_repo(monkeypatch):
    class DummyRepo:
        def __init__(self, session):
            self.session = session

    monkeypatch.setattr(dependencies, "SQLAlchemyUserRepository", DummyRepo)

    session = object()
    repo = await dependencies.get_user_repository(db=session)
    assert isinstance(repo, DummyRepo)
    assert repo.session is session


@pytest.mark.asyncio
async def test_get_current_user_success(monkeypatch):
    async_mock = AsyncMock(
        return_value=UserOutput(
            id=uuid4(),
            email="john@example.com",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )
    )

    class DummyUseCase:
        def __init__(self, user_repository, jwt_secret):
            self.user_repository = user_repository
            self.jwt_secret = jwt_secret

        get_user_from_token = async_mock

    monkeypatch.setattr(dependencies, "LoginUserUseCase", DummyUseCase)

    credentials = SimpleNamespace(credentials="token")
    settings = Settings(JWT_SECRET="secret")
    response = await dependencies.get_current_user(credentials, object(), settings)

    assert response.email == "john@example.com"
    async_mock.assert_awaited_once_with("token")


@pytest.mark.asyncio
async def test_get_current_user_invalid_token_raises_401(monkeypatch):
    class DummyUseCase:
        def __init__(self, user_repository, jwt_secret):
            pass

        async def get_user_from_token(self, token):
            raise InvalidCredentialsError("bad token")

    monkeypatch.setattr(dependencies, "LoginUserUseCase", DummyUseCase)

    credentials = SimpleNamespace(credentials="token")
    settings = Settings(JWT_SECRET="secret")

    with pytest.raises(HTTPException) as exc:
        await dependencies.get_current_user(credentials, object(), settings)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_get_current_user_inactive_user_raises_403(monkeypatch):
    class DummyUseCase:
        def __init__(self, user_repository, jwt_secret):
            pass

        async def get_user_from_token(self, token):
            raise UserInactiveError("inactive")

    monkeypatch.setattr(dependencies, "LoginUserUseCase", DummyUseCase)

    credentials = SimpleNamespace(credentials="token")
    settings = Settings(JWT_SECRET="secret")

    with pytest.raises(HTTPException) as exc:
        await dependencies.get_current_user(credentials, object(), settings)

    assert exc.value.status_code == 403
    assert exc.value.detail == "User account is inactive"

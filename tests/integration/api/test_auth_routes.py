from datetime import datetime, UTC
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

from auth_service.domain.entities.user import User
from auth_service.infrastructure.adapters.input.api.dependencies import (
    get_current_user,
    get_settings,
    get_user_repository,
)
from auth_service.infrastructure.adapters.input.api.main import create_app
from auth_service.infrastructure.adapters.input.api.schemas.auth import UserResponse
from auth_service.infrastructure.config import Settings
from video_processor_shared.domain.value_objects import Email, Password


class FakeUserRepository:
    def __init__(self):
        self._users_by_email = {}
        self._users_by_id = {}

    async def save(self, user: User) -> User:
        self._users_by_email[user.email.value] = user
        self._users_by_id[user.id] = user
        return user

    async def find_by_id(self, user_id):
        return self._users_by_id.get(user_id)

    async def find_by_email(self, email):
        return self._users_by_email.get(email.lower())

    async def update(self, user: User) -> User:
        self._users_by_email[user.email.value] = user
        self._users_by_id[user.id] = user
        return user

    async def delete(self, user_id):
        user = self._users_by_id.pop(user_id, None)
        if not user:
            return False
        self._users_by_email.pop(user.email.value, None)
        return True


def build_user(email: str = "john@example.com", active: bool = True) -> User:
    return User(
        id=uuid4(),
        email=Email(email),
        password=Password.create("StrongPass123!"),
        full_name="John Doe",
        is_active=active,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def create_test_client(repo: FakeUserRepository, monkeypatch) -> TestClient:
    async def fake_init_db():
        return None

    monkeypatch.setattr("auth_service.infrastructure.adapters.input.api.main.init_db", fake_init_db)
    app = create_app()

    async def override_repo():
        return repo

    def override_settings():
        return Settings(JWT_SECRET="test-secret", JWT_EXPIRATION_HOURS=1)

    app.dependency_overrides[get_user_repository] = override_repo
    app.dependency_overrides[get_settings] = override_settings

    return TestClient(app)


def test_register_login_me_validate_and_get_user_by_id(monkeypatch):
    repo = FakeUserRepository()
    with create_test_client(repo, monkeypatch) as client:
        register_response = client.post(
            "/auth/register",
            json={
                "email": "john@example.com",
                "password": "StrongPass123!",
                "full_name": " John Doe ",
            },
        )
        assert register_response.status_code == 201
        body = register_response.json()
        assert body["email"] == "john@example.com"
        assert body["full_name"] == "John Doe"

        login_response = client.post(
            "/auth/login",
            json={"email": "john@example.com", "password": "StrongPass123!"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        validate_response = client.post("/auth/validate", params={"token": token})
        assert validate_response.status_code == 200
        assert validate_response.json() == {"valid": True}

        user_id = body["id"]
        user_by_id = client.get(f"/auth/users/{user_id}")
        assert user_by_id.status_code == 200
        assert user_by_id.json()["email"] == "john@example.com"

        async def override_current_user():
            return UserResponse(
                id=uuid4(),
                email="me@example.com",
                full_name="Me",
                is_active=True,
                created_at=datetime.now(UTC),
            )

        client.app.dependency_overrides[get_current_user] = override_current_user
        me_response = client.get("/auth/me", headers={"Authorization": "Bearer any"})
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "me@example.com"


def test_register_conflict_and_login_error_paths(monkeypatch):
    repo = FakeUserRepository()
    existing = build_user("existing@example.com")

    async_save = AsyncMock(return_value=existing)
    repo.save = async_save

    async_find_by_email = AsyncMock(side_effect=[existing, existing, build_user("inactive@example.com", active=False)])
    repo.find_by_email = async_find_by_email

    with create_test_client(repo, monkeypatch) as client:
        conflict_response = client.post(
            "/auth/register",
            json={
                "email": "existing@example.com",
                "password": "StrongPass123!",
                "full_name": "Existing",
            },
        )
        assert conflict_response.status_code == 409

        invalid_credentials = client.post(
            "/auth/login",
            json={"email": "existing@example.com", "password": "WrongPass123!"},
        )
        assert invalid_credentials.status_code == 401

        inactive_user = client.post(
            "/auth/login",
            json={"email": "inactive@example.com", "password": "StrongPass123!"},
        )
        assert inactive_user.status_code == 403


def test_get_user_by_id_not_found_and_validate_false(monkeypatch):
    repo = FakeUserRepository()
    user = build_user()

    async_find_by_id = AsyncMock(return_value=None)
    repo.find_by_id = async_find_by_id

    async_find_by_email = AsyncMock(return_value=user)
    repo.find_by_email = async_find_by_email

    with create_test_client(repo, monkeypatch) as client:
        missing_user = client.get(f"/auth/users/{uuid4()}")
        assert missing_user.status_code == 404

        invalid = client.post("/auth/validate", params={"token": "broken.token"})
        assert invalid.status_code == 200
        assert invalid.json() == {"valid": False}

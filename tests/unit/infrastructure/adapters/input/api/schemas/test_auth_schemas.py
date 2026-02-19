from datetime import datetime, UTC
from uuid import uuid4

import pytest
from pydantic import ValidationError

from auth_service.infrastructure.adapters.input.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


def test_register_request_validators_trim_name_and_validate_password():
    request = RegisterRequest(
        email="john@example.com",
        password="StrongPass123!",
        full_name="  John Doe  ",
    )
    assert request.full_name == "John Doe"

    with pytest.raises(ValidationError):
        RegisterRequest(
            email="john@example.com",
            password="short",
            full_name="John Doe",
        )

    with pytest.raises(ValidationError):
        RegisterRequest(
            email="john@example.com",
            password="StrongPass123!",
            full_name="J",
        )


def test_login_and_response_schemas():
    login = LoginRequest(email="john@example.com", password="StrongPass123!")
    assert login.email == "john@example.com"

    token = TokenResponse(access_token="token", expires_in=3600)
    assert token.token_type == "bearer"

    user_response = UserResponse(
        id=uuid4(),
        email="john@example.com",
        full_name="John Doe",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    assert user_response.is_active is True

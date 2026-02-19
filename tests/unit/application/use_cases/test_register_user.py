from datetime import datetime, UTC
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from auth_service.application.ports.input.auth_service import RegisterInput
from auth_service.application.use_cases.register_user import RegisterUserUseCase
from auth_service.domain.entities.user import User
from video_processor_shared.domain.exceptions import UserAlreadyExistsError
from video_processor_shared.domain.value_objects import Email, Password


@pytest.mark.asyncio
async def test_register_user_success():
    repository = AsyncMock()
    repository.find_by_email.return_value = None

    saved_user = User(
        id=uuid4(),
        email=Email("john@example.com"),
        password=Password.create("StrongPass123!"),
        full_name="John Doe",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    repository.save.return_value = saved_user

    use_case = RegisterUserUseCase(repository)
    result = await use_case.execute(
        RegisterInput(
            email="john@example.com",
            password="StrongPass123!",
            full_name="  John Doe  ",
        )
    )

    repository.find_by_email.assert_awaited_once_with("john@example.com")
    repository.save.assert_awaited_once()
    assert result.email == "john@example.com"
    assert result.full_name == "John Doe"


@pytest.mark.asyncio
async def test_register_user_raises_when_email_exists():
    repository = AsyncMock()
    repository.find_by_email.return_value = object()

    use_case = RegisterUserUseCase(repository)

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(
            RegisterInput(
                email="already@example.com",
                password="StrongPass123!",
                full_name="Already",
            )
        )

    repository.save.assert_not_called()

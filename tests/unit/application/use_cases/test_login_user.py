from datetime import datetime, UTC
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from auth_service.application.ports.input.auth_service import LoginInput
from auth_service.application.use_cases.login_user import LoginUserUseCase
from auth_service.domain.entities.user import User
from video_processor_shared.domain.exceptions import InvalidCredentialsError, UserInactiveError
from video_processor_shared.domain.value_objects import Email, Password


def build_user(active: bool = True) -> User:
    return User(
        id=uuid4(),
        email=Email("john@example.com"),
        password=Password.create("StrongPass123!"),
        full_name="John Doe",
        is_active=active,
    )


@pytest.mark.asyncio
async def test_login_success_generates_bearer_token():
    repository = AsyncMock()
    repository.find_by_email.return_value = build_user()
    use_case = LoginUserUseCase(repository, jwt_secret="secret", jwt_expiration_hours=1)

    output = await use_case.execute(
        LoginInput(email="john@example.com", password="StrongPass123!")
    )

    assert output.token_type == "bearer"
    assert output.expires_in == 3600
    assert output.access_token.count(".") == 2


@pytest.mark.asyncio
async def test_login_invalid_email_raises_invalid_credentials():
    repository = AsyncMock()
    use_case = LoginUserUseCase(repository)

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(LoginInput(email="invalid", password="StrongPass123!"))


@pytest.mark.asyncio
async def test_login_user_not_found_raises_invalid_credentials():
    repository = AsyncMock()
    repository.find_by_email.return_value = None
    use_case = LoginUserUseCase(repository)

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(
            LoginInput(email="john@example.com", password="StrongPass123!")
        )


@pytest.mark.asyncio
async def test_login_wrong_password_raises_invalid_credentials():
    repository = AsyncMock()
    repository.find_by_email.return_value = build_user()
    use_case = LoginUserUseCase(repository)

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(
            LoginInput(email="john@example.com", password="WrongPass123!")
        )


@pytest.mark.asyncio
async def test_login_inactive_user_raises_user_inactive():
    repository = AsyncMock()
    repository.find_by_email.return_value = build_user(active=False)
    use_case = LoginUserUseCase(repository)

    with pytest.raises(UserInactiveError):
        await use_case.execute(
            LoginInput(email="john@example.com", password="StrongPass123!")
        )


@pytest.mark.asyncio
async def test_get_user_from_token_success():
    repository = AsyncMock()
    user = build_user()
    repository.find_by_id.return_value = user
    use_case = LoginUserUseCase(repository, jwt_secret="secret")

    token = use_case._generate_token(str(user.id), user.email.value, 3600)
    output = await use_case.get_user_from_token(token)

    assert output.id == user.id
    assert output.email == user.email.value


@pytest.mark.asyncio
async def test_get_user_from_token_invalid_or_expired_or_missing_sub():
    repository = AsyncMock()
    use_case = LoginUserUseCase(repository, jwt_secret="secret")

    with pytest.raises(InvalidCredentialsError):
        await use_case.get_user_from_token("invalid.token")

    expired_token = use_case._generate_token(str(uuid4()), "john@example.com", -1)
    with pytest.raises(InvalidCredentialsError):
        await use_case.get_user_from_token(expired_token)

    token_without_sub = use_case._generate_token(str(uuid4()), "john@example.com", 3600)
    payload = use_case._decode_token(token_without_sub)
    payload.pop("sub", None)
    forged = use_case._generate_token(str(uuid4()), "john@example.com", 3600)
    forged_payload = use_case._decode_token(forged)
    forged_payload["sub"] = None

    original_decode = use_case._decode_token
    use_case._decode_token = lambda _token: {"sub": None, "exp": datetime.now(UTC).timestamp() + 60}
    with pytest.raises(InvalidCredentialsError):
        await use_case.get_user_from_token("any")
    use_case._decode_token = original_decode


@pytest.mark.asyncio
async def test_get_user_from_token_user_not_found_or_inactive():
    repository = AsyncMock()
    user = build_user()
    use_case = LoginUserUseCase(repository, jwt_secret="secret")
    token = use_case._generate_token(str(user.id), user.email.value, 3600)

    repository.find_by_id.return_value = None
    with pytest.raises(InvalidCredentialsError):
        await use_case.get_user_from_token(token)

    repository.find_by_id.return_value = build_user(active=False)
    with pytest.raises(UserInactiveError):
        await use_case.get_user_from_token(token)


@pytest.mark.asyncio
async def test_validate_token_true_false_and_exception_path():
    repository = AsyncMock()
    use_case = LoginUserUseCase(repository, jwt_secret="secret")

    valid_token = use_case._generate_token(str(uuid4()), "john@example.com", 60)
    assert await use_case.validate_token(valid_token) is True
    assert await use_case.validate_token("bad.token") is False

    old_decode = use_case._decode_token
    use_case._decode_token = lambda _token: (_ for _ in ()).throw(RuntimeError("boom"))
    assert await use_case.validate_token("anything") is False
    use_case._decode_token = old_decode


def test_decode_token_returns_none_on_bad_signature_and_invalid_format():
    repository = AsyncMock()
    use_case = LoginUserUseCase(repository, jwt_secret="secret")

    assert use_case._decode_token("bad-format") is None

    token = use_case._generate_token(str(uuid4()), "john@example.com", 60)
    bad_signature_token = token.rsplit(".", 1)[0] + ".tampered"
    assert use_case._decode_token(bad_signature_token) is None


def test_generate_token_contains_expected_expiration_window():
    repository = AsyncMock()
    use_case = LoginUserUseCase(repository, jwt_secret="secret")

    token = use_case._generate_token(str(uuid4()), "john@example.com", 120)
    payload = use_case._decode_token(token)

    now_ts = int(datetime.now(UTC).timestamp())
    assert payload is not None
    assert payload["exp"] >= now_ts + 100
    assert payload["exp"] <= now_ts + 130

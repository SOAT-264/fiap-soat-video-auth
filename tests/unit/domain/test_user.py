from datetime import datetime, UTC
from uuid import uuid4

from auth_service.domain.entities.user import User
from video_processor_shared.domain.value_objects import Email, Password


def build_user() -> User:
    return User(
        id=uuid4(),
        email=Email("john@example.com"),
        password=Password.create("StrongPass123!"),
        full_name="John Doe",
    )


def test_user_validate_password_success_and_failure():
    user = build_user()

    assert user.validate_password("StrongPass123!") is True
    assert user.validate_password("wrong-password") is False


def test_user_activate_deactivate_update_name_and_change_password():
    user = build_user()
    original_updated_at = user.updated_at

    user.deactivate()
    assert user.is_active is False
    assert user.updated_at >= original_updated_at

    user.activate()
    assert user.is_active is True

    user.update_name("Jane Doe")
    assert user.full_name == "Jane Doe"

    user.change_password(Password.create("AnotherPass123!"))
    assert user.validate_password("AnotherPass123!") is True


def test_user_equality_hash_and_repr():
    same_id = uuid4()
    now = datetime.now(UTC)
    user_1 = User(
        id=same_id,
        email=Email("a@example.com"),
        password=Password.create("StrongPass123!"),
        full_name="A",
        created_at=now,
        updated_at=now,
    )
    user_2 = User(
        id=same_id,
        email=Email("b@example.com"),
        password=Password.create("StrongPass123!"),
        full_name="B",
        created_at=now,
        updated_at=now,
    )

    assert user_1 == user_2
    assert hash(user_1) == hash(user_2)
    assert user_1 != object()
    assert "User(id=" in repr(user_1)

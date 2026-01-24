"""User Entity."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from video_processor_shared.domain.value_objects import Email, Password


class User:
    """
    User Entity - Represents a system user.

    This is a domain entity with identity and behavior.
    """

    def __init__(
        self,
        id: UUID,
        email: Email,
        password: Password,
        full_name: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """Initialize a User entity."""
        self.id = id
        self.email = email
        self.password = password
        self.full_name = full_name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def validate_password(self, plain_password: str) -> bool:
        """Validate if the given password matches."""
        return self.password.verify(plain_password)

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def update_name(self, full_name: str) -> None:
        """Update user's full name."""
        self.full_name = full_name
        self.updated_at = datetime.utcnow()

    def change_password(self, new_password: Password) -> None:
        """Change user's password."""
        self.password = new_password
        self.updated_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email})"

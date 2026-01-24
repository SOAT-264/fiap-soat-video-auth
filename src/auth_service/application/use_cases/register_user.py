"""Register User Use Case."""
from uuid import uuid4

from auth_service.domain.entities.user import User
from auth_service.application.ports.input.auth_service import RegisterInput, UserOutput
from auth_service.application.ports.output.repositories.user_repository import IUserRepository

from video_processor_shared.domain.value_objects import Email, Password
from video_processor_shared.domain.exceptions import UserAlreadyExistsError


class RegisterUserUseCase:
    """Use Case: Register a new user."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository

    async def execute(self, input_data: RegisterInput) -> UserOutput:
        """Execute the registration use case."""
        # Create Value Objects (validates format)
        email = Email(input_data.email)
        password = Password.create(input_data.password)

        # Check if user already exists
        existing_user = await self._user_repository.find_by_email(email.value)
        if existing_user:
            raise UserAlreadyExistsError(f"User with email {email.value} already exists")

        # Create User entity
        user = User(
            id=uuid4(),
            email=email,
            password=password,
            full_name=input_data.full_name.strip(),
            is_active=True,
        )

        # Persist user
        saved_user = await self._user_repository.save(user)

        return UserOutput(
            id=saved_user.id,
            email=saved_user.email.value,
            full_name=saved_user.full_name,
            is_active=saved_user.is_active,
            created_at=saved_user.created_at,
        )

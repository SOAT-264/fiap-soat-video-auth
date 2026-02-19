"""Login User Use Case."""
from datetime import datetime, timedelta, UTC
from typing import Optional
from uuid import UUID
import hashlib
import hmac
import json
import base64

from auth_service.application.ports.input.auth_service import (
    LoginInput,
    AuthTokenOutput,
    UserOutput,
)
from auth_service.application.ports.output.repositories.user_repository import IUserRepository

from video_processor_shared.domain.value_objects import Email
from video_processor_shared.domain.exceptions import (
    InvalidCredentialsError,
    UserInactiveError,
)


class LoginUserUseCase:
    """Use Case: Authenticate a user."""

    def __init__(
        self,
        user_repository: IUserRepository,
        jwt_secret: str = "default-secret",
        jwt_expiration_hours: int = 24,
    ):
        self._user_repository = user_repository
        self._jwt_secret = jwt_secret
        self._jwt_expiration_hours = jwt_expiration_hours

    async def execute(self, input_data: LoginInput) -> AuthTokenOutput:
        """Execute the login use case."""
        try:
            email = Email(input_data.email)
        except Exception:
            raise InvalidCredentialsError("Invalid credentials")

        user = await self._user_repository.find_by_email(email.value)
        if not user:
            raise InvalidCredentialsError("Invalid credentials")

        if not user.validate_password(input_data.password):
            raise InvalidCredentialsError("Invalid credentials")

        if not user.is_active:
            raise UserInactiveError("User account is inactive")

        expires_in = self._jwt_expiration_hours * 3600
        token = self._generate_token(
            user_id=str(user.id),
            email=user.email.value,
            expires_in=expires_in,
        )

        return AuthTokenOutput(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
        )

    async def get_user_from_token(self, token: str) -> UserOutput:
        """Get user from JWT token."""
        payload = self._decode_token(token)
        if not payload:
            raise InvalidCredentialsError("Invalid token")

        exp = payload.get("exp", 0)
        if datetime.now(UTC).timestamp() > exp:
            raise InvalidCredentialsError("Token expired")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentialsError("Invalid token")

        user = await self._user_repository.find_by_id(UUID(user_id))
        if not user:
            raise InvalidCredentialsError("User not found")

        if not user.is_active:
            raise UserInactiveError("User account is inactive")

        return UserOutput(
            id=user.id,
            email=user.email.value,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    async def validate_token(self, token: str) -> bool:
        """Validate if token is valid."""
        try:
            payload = self._decode_token(token)
            if not payload:
                return False
            exp = payload.get("exp", 0)
            return datetime.now(UTC).timestamp() <= exp
        except Exception:
            return False

    def _generate_token(self, user_id: str, email: str, expires_in: int) -> str:
        """Generate a JWT token."""
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).rstrip(b"=").decode()

        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "email": email,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
        }
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).rstrip(b"=").decode()

        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._jwt_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def _decode_token(self, token: str) -> Optional[dict]:
        """Decode and validate a JWT token."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts

            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._jwt_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            expected_signature_b64 = base64.urlsafe_b64encode(
                expected_signature
            ).rstrip(b"=").decode()

            if not hmac.compare_digest(signature_b64, expected_signature_b64):
                return None

            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding

            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            return payload

        except Exception:
            return None

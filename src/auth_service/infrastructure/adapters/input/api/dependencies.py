"""API Dependencies."""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth_service.infrastructure.config import Settings, get_settings
from auth_service.application.ports.output.repositories import IUserRepository
from auth_service.infrastructure.adapters.output.persistence.repositories import (
    SQLAlchemyUserRepository,
)
from auth_service.infrastructure.adapters.output.persistence.database import get_db
from auth_service.application.use_cases import LoginUserUseCase
from auth_service.infrastructure.adapters.input.api.schemas.auth import UserResponse

from video_processor_shared.domain.exceptions import InvalidCredentialsError, UserInactiveError

security = HTTPBearer()


async def get_user_repository(
    db=Depends(get_db),
) -> IUserRepository:
    """Get user repository instance."""
    return SQLAlchemyUserRepository(db)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserResponse:
    """Get current authenticated user from token."""
    try:
        use_case = LoginUserUseCase(
            user_repository=user_repository,
            jwt_secret=settings.JWT_SECRET,
        )
        user = await use_case.get_user_from_token(credentials.credentials)
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

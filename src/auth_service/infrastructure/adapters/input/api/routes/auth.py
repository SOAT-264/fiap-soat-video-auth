"""Auth API Routes."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends

from auth_service.application.use_cases import RegisterUserUseCase, LoginUserUseCase
from auth_service.application.ports.input.auth_service import RegisterInput, LoginInput
from auth_service.infrastructure.adapters.input.api.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from auth_service.infrastructure.adapters.input.api.dependencies import (
    get_user_repository,
    get_settings,
    get_current_user,
)
from auth_service.application.ports.output.repositories import IUserRepository
from auth_service.infrastructure.config import Settings

from video_processor_shared.domain.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserInactiveError,
    InvalidEmailError,
    WeakPasswordError,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
):
    """Register a new user."""
    try:
        use_case = RegisterUserUseCase(user_repository=user_repository)
        result = await use_case.execute(
            RegisterInput(
                email=request.email,
                password=request.password,
                full_name=request.full_name,
            )
        )
        return UserResponse(
            id=result.id,
            email=result.email,
            full_name=result.full_name,
            is_active=result.is_active,
            created_at=result.created_at,
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidEmailError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except WeakPasswordError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    """Authenticate user and receive JWT token."""
    try:
        use_case = LoginUserUseCase(
            user_repository=user_repository,
            jwt_secret=settings.JWT_SECRET,
            jwt_expiration_hours=settings.JWT_EXPIRATION_HOURS,
        )
        result = await use_case.execute(
            LoginInput(email=request.email, password=request.password)
        )
        return TokenResponse(
            access_token=result.access_token,
            token_type=result.token_type,
            expires_in=result.expires_in,
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """Get current authenticated user information."""
    return current_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
):
    """Get user by ID (internal use)."""
    user = await user_repository.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(
        id=user.id,
        email=user.email.value,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/validate")
async def validate_token(
    token: str,
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    """Validate a JWT token (for inter-service communication)."""
    use_case = LoginUserUseCase(
        user_repository=user_repository,
        jwt_secret=settings.JWT_SECRET,
    )
    is_valid = await use_case.validate_token(token)
    return {"valid": is_valid}

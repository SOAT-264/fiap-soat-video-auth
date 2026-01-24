"""API Routes."""
from auth_service.infrastructure.adapters.input.api.routes.auth import router as auth_router
from auth_service.infrastructure.adapters.input.api.routes.health import router as health_router

__all__ = ["auth_router", "health_router"]

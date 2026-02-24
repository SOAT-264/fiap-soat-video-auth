"""FastAPI Application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from auth_service.infrastructure.adapters.input.api.routes import auth_router, health_router
from auth_service.infrastructure.adapters.output.persistence.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    await init_db()
    yield


def create_app() -> FastAPI:
    """Create FastAPI application."""

    app = FastAPI(
        title="Auth Service",
        description="Authentication microservice for Video Processor",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(health_router)
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    app.mount("/metrics", make_asgi_app())

    return app


app = create_app()

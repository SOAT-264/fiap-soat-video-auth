"""Health Check Routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth-service"}


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready"}

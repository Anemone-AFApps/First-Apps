"""Status and observability endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter


router = APIRouter(prefix="/status", tags=["status"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Provide a basic health probe for orchestration and uptime monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

"""Status and observability endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ..dependencies import get_trending_service
from ..services.trending.service import TrendingService


router = APIRouter(prefix="/status", tags=["status"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Provide a basic health probe for orchestration and uptime monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/insights")
async def service_insights(
    service: TrendingService = Depends(get_trending_service),
) -> dict[str, object]:
    """Expose trending service health snapshots for dashboards."""
    return service.snapshot()

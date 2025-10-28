"""Endpoints exposing aggregated trending insights."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..dependencies import get_trending_service
from ..services.trending.service import TrendingService

router = APIRouter(prefix="/trending", tags=["trending"])


@router.get("/")
async def list_trending(
    limit: int | None = Query(None, ge=1, le=100, description="Maximum number of items to return."),
    service: TrendingService = Depends(get_trending_service),
) -> dict[str, object]:
    """Return a curated set of trending artefacts from multiple public sources."""
    items = await service.fetch_trending(limit=limit)
    return {
        "count": len(items),
        "limit": limit or service.default_limit,
        "items": [item.to_dict() for item in items],
    }


@router.get("/sources")
async def trending_sources(
    service: TrendingService = Depends(get_trending_service),
) -> dict[str, object]:
    """Provide health and diagnostic information for each data provider."""
    health = await service.get_source_health()
    return {
        "sources": [entry.to_dict() for entry in health],
        "service": service.snapshot(),
    }

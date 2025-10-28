"""Shared dependency injection helpers for FastAPI routers."""
from __future__ import annotations

from fastapi import Depends

from .core.settings import Settings, get_settings
from .services.trending.service import TrendingService, build_trending_service


def get_app_settings() -> Settings:
    """Expose app settings for request handlers."""
    return get_settings()


def get_trending_service(
    settings: Settings = Depends(get_app_settings),
) -> TrendingService:
    """Provide the configured trending aggregation service."""
    return build_trending_service(settings)

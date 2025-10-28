"""Core service entry point for the automation platform."""
from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from .core.settings import get_settings
from .routers import status, trending
from .services.trending.service import build_trending_service


logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage lifecycle resources such as background discovery tasks."""
    trending_service = build_trending_service(settings)
    application.state.trending_service = trending_service
    logger.info("Priming trending service cache")
    await trending_service.fetch_trending(force_refresh=True)
    trending_service.register_background_tasks()
    try:
        yield
    finally:
        await trending_service.shutdown()


app = FastAPI(
    title=settings.app_name,
    description="Service gateway for orchestrating automation and autonomous discovery workflows.",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(status.router)
app.include_router(trending.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint that advertises service capabilities."""
    return {
        "message": f"{settings.app_name} is online",
        "docs": "/docs",
        "status": "/status/health",
        "trending": "/trending",
    }

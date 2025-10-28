"""Core service entry point for the automation platform."""
from fastapi import FastAPI

from .routers import status


app = FastAPI(
    title="Autonomous Platform Core API",
    description="Service gateway for orchestrating automation and self-healing workflows.",
    version="0.1.0",
)

app.include_router(status.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint that advertises service capabilities."""
    return {
        "message": f"{settings.app_name} is online",
        "docs": "/docs",
        "status": "/status/health",
        "trending": "/trending",
        "message": "Autonomous platform is online",
        "docs": "/docs",
        "status": "/status/health",
    }

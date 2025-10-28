"""Application configuration models and helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field, PositiveInt, validator


class Settings(BaseSettings):
    """Central configuration driven by environment variables."""

    app_name: str = Field(
        "Autonomous Discovery Service",
        description="Human readable service name used in documentation and metadata.",
    )
    trending_default_limit: PositiveInt = Field(
        10,
        description="Default number of trending items to return when no limit is provided.",
        env="TRENDING_DEFAULT_LIMIT",
    )
    trending_refresh_seconds: PositiveInt = Field(
        900,
        description="Interval in seconds for refreshing cached trending data.",
        env="TRENDING_REFRESH_SECONDS",
    )
    trending_sources: List[str] = Field(
        default_factory=lambda: ["reddit", "hackernews", "github"],
        description="Ordered list of trending data sources to activate.",
        env="TRENDING_SOURCES",
    )
    http_timeout_seconds: PositiveInt = Field(
        10,
        description="Timeout applied to outbound HTTP calls for data collection.",
        env="HTTP_TIMEOUT_SECONDS",
    )

    class Config:
        env_prefix = "APP_"
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("trending_sources", pre=True)
    def _split_sources(cls, value: object) -> List[str]:  # type: ignore[override]
        """Allow comma-separated configuration strings or lists."""
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        if isinstance(value, (list, tuple)):
            return [str(part).strip() for part in value if str(part).strip()]
        raise ValueError("Unsupported type for trending sources configuration")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Provide a cached Settings instance suitable for dependency injection."""
    return Settings()

"""Domain models for trending discovery."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class TrendingItem:
    """Normalized representation of a single trending entity."""

    title: str
    url: str
    source: str
    score: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the item into a JSON-serialisable payload."""
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "score": self.score,
            "metadata": dict(self.metadata),
        }


@dataclass
class SourceHealth:
    """Track heartbeat metadata for a source to aid self-healing flows."""

    source: str
    status: str
    message: str | None = None
    last_success_at: datetime | None = None
    last_error_at: datetime | None = None

    @classmethod
    def ok(cls, source: str) -> "SourceHealth":
        now = datetime.now(timezone.utc)
        return cls(source=source, status="ok", last_success_at=now, message=None)

    @classmethod
    def error(cls, source: str, message: str) -> "SourceHealth":
        now = datetime.now(timezone.utc)
        return cls(source=source, status="error", message=message, last_error_at=now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "status": self.status,
            "message": self.message,
            "last_success_at": self.last_success_at.isoformat() if self.last_success_at else None,
            "last_error_at": self.last_error_at.isoformat() if self.last_error_at else None,
        }

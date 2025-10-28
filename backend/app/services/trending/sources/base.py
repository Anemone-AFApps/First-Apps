"""Abstract interfaces and helpers for trending data sources."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import TrendingItem


class TrendingSource(ABC):
    """Base class for adapters that fetch trending artefacts from external systems."""

    name: str
    weight: float = 1.0

    @abstractmethod
    async def fetch(self, limit: int) -> list[TrendingItem]:
        """Collect trending items from the upstream provider."""

    def __repr__(self) -> str:  # pragma: no cover - debugging helper only
        return f"{self.__class__.__name__}(name={self.name!r}, weight={self.weight})"

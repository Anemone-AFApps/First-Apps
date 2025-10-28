"""Trending aggregation orchestration."""
from __future__ import annotations

import asyncio
import logging
from collections import OrderedDict
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Awaitable, Callable, Dict, Iterable, List, Optional

from ...core.settings import Settings
from .models import SourceHealth, TrendingItem
from .sources.base import TrendingSource
from .sources.github import GitHubTrendingSource
from .sources.hackernews import HackerNewsTrendingSource
from .sources.reddit import RedditTrendingSource

logger = logging.getLogger(__name__)


@dataclass
class _CacheEntry:
    items: List[TrendingItem]
    expires_at: datetime

    def is_valid(self) -> bool:
        return datetime.now(timezone.utc) < self.expires_at


SOURCE_FACTORIES: Dict[str, Callable[[float], TrendingSource]] = {
    "reddit": lambda timeout: RedditTrendingSource(timeout=timeout),
    "hackernews": lambda timeout: HackerNewsTrendingSource(timeout=timeout),
    "github": lambda timeout: GitHubTrendingSource(timeout=timeout),
}


class TrendingService:
    """Coordinate retrieval and caching of trending items across sources."""

    def __init__(
        self,
        sources: Iterable[TrendingSource],
        *,
        default_limit: int,
        refresh_interval_seconds: int,
    ) -> None:
        self._sources = list(sources)
        self._default_limit = default_limit
        self._refresh_interval_seconds = refresh_interval_seconds
        self._cache: Dict[int, _CacheEntry] = {}
        self._cache_lock = asyncio.Lock()
        self._source_health: Dict[str, SourceHealth] = {
            source.name: SourceHealth(source=source.name, status="unknown")
            for source in self._sources
        }
        self._background_task: asyncio.Task[None] | None = None
        self._shutdown = asyncio.Event()
        self._last_refresh_at: datetime | None = None

    @property
    def default_limit(self) -> int:
        return self._default_limit

    def register_background_tasks(self) -> None:
        """Ensure the periodic refresher is running."""
        if self._background_task and not self._background_task.done():
            return
        self._shutdown.clear()
        self._background_task = asyncio.create_task(self._periodic_refresh())

    async def shutdown(self) -> None:
        """Stop background tasks and wait for completion."""
        self._shutdown.set()
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:  # pragma: no cover - expected cancellation flow
                pass
            finally:
                self._background_task = None

    async def fetch_trending(
        self,
        *,
        limit: Optional[int] = None,
        force_refresh: bool = False,
    ) -> List[TrendingItem]:
        """Return a consolidated view of trending items respecting caches."""
        limit = limit or self._default_limit
        async with self._cache_lock:
            entry = self._cache.get(limit)
            if entry and entry.is_valid() and not force_refresh:
                return entry.items[:limit]

        items = await self._refresh(limit)
        return items[:limit]

    async def get_source_health(self) -> List[SourceHealth]:
        return list(self._source_health.values())

    async def _refresh(self, limit: int) -> List[TrendingItem]:
        """Collect fresh data for the requested limit."""
        fetch_limit = max(limit, self._default_limit)
        logger.debug("Refreshing trending cache for limit=%s", fetch_limit)

        tasks: list[Awaitable[list[TrendingItem]]] = [
            self._fetch_source(source, fetch_limit) for source in self._sources
        ]
        results = await asyncio.gather(*tasks)

        merged = self._merge_results(results)
        ttl = timedelta(seconds=self._refresh_interval_seconds)
        expires_at = datetime.now(timezone.utc) + ttl
        entry = _CacheEntry(items=merged, expires_at=expires_at)
        async with self._cache_lock:
            self._cache[fetch_limit] = entry
            self._cache[limit] = entry
            self._last_refresh_at = datetime.now(timezone.utc)
        return merged

    async def _fetch_source(self, source: TrendingSource, limit: int) -> list[TrendingItem]:
        try:
            items = await source.fetch(limit)
            weighted = [
                replace(
                    item,
                    score=item.score * source.weight,
                    metadata={**dict(item.metadata), "raw_score": item.score},
                )
                for item in items
            ]
            self._source_health[source.name] = SourceHealth.ok(source.name)
            return weighted
        except Exception as exc:  # pragma: no cover - network failures are environment specific
            message = f"{source.name} fetch failed: {exc}"
            logger.warning(message)
            self._source_health[source.name] = SourceHealth.error(source.name, message)
            return []

    def _merge_results(self, results: Iterable[list[TrendingItem]]) -> List[TrendingItem]:
        """Merge, deduplicate, and order results by weighted score."""
        aggregated: Dict[str, TrendingItem] = OrderedDict()
        for items in results:
            for item in items:
                key = item.url.lower()
                existing = aggregated.get(key)
                if existing and existing.score >= item.score:
                    continue
                aggregated[key] = item

        sorted_items = sorted(
            aggregated.values(),
            key=lambda item: item.score,
            reverse=True,
        )
        return sorted_items

    async def _periodic_refresh(self) -> None:
        logger.info(
            "Starting trending refresh loop (interval=%ss)",
            self._refresh_interval_seconds,
        )
        try:
            while not self._shutdown.is_set():
                try:
                    await self.fetch_trending(force_refresh=True)
                except Exception:  # pragma: no cover - protective guard
                    logger.exception("Trending refresh cycle failed")
                try:
                    await asyncio.wait_for(
                        self._shutdown.wait(), timeout=self._refresh_interval_seconds
                    )
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:  # pragma: no cover - shutdown flow
            logger.info("Trending refresh loop cancelled")
            raise

    def snapshot(self) -> dict[str, object]:
        """Provide status metadata for observability endpoints."""
        return {
            "default_limit": self._default_limit,
            "refresh_interval_seconds": self._refresh_interval_seconds,
            "last_refresh_at": self._last_refresh_at.isoformat()
            if self._last_refresh_at
            else None,
            "sources": [health.to_dict() for health in self._source_health.values()],
            "cached_limits": sorted(self._cache.keys()),
        }


_service_singleton: TrendingService | None = None


def build_trending_service(settings: Settings) -> TrendingService:
    """Create or reuse the configured TrendingService singleton."""
    global _service_singleton
    if _service_singleton is None:
        timeout = float(settings.http_timeout_seconds)
        sources = [
            SOURCE_FACTORIES[name](timeout)
            for name in settings.trending_sources
            if name in SOURCE_FACTORIES
        ]
        missing = set(settings.trending_sources) - set(SOURCE_FACTORIES)
        if missing:
            logger.warning("Unknown trending sources skipped: %s", ", ".join(sorted(missing)))
        _service_singleton = TrendingService(
            sources,
            default_limit=settings.trending_default_limit,
            refresh_interval_seconds=settings.trending_refresh_seconds,
        )
    return _service_singleton

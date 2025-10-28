"""Unit coverage for the trending aggregation service."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

from backend.app.services.trending.models import TrendingItem
from backend.app.services.trending.service import TrendingService


@dataclass
class StubSource:
    name: str
    weight: float = 1.0

    def __init__(self, name: str, items: list[TrendingItem]):
        self.name = name
        self._items = items

    async def fetch(self, limit: int) -> list[TrendingItem]:
        await asyncio.sleep(0)  # simulate async boundary
        return self._items[:limit]


def test_trending_service_respects_limit_and_order():
    async def scenario() -> None:
        source_a = StubSource(
            "source_a",
            [
                TrendingItem(title="A", url="https://a", source="source_a", score=10),
                TrendingItem(title="B", url="https://b", source="source_a", score=8),
            ],
        )
        source_b = StubSource(
            "source_b",
            [
                TrendingItem(title="C", url="https://c", source="source_b", score=12),
                TrendingItem(title="B", url="https://b", source="source_b", score=15),
            ],
        )
        service = TrendingService(
            [source_a, source_b],
            default_limit=5,
            refresh_interval_seconds=60,
        )

        results = await service.fetch_trending(limit=3, force_refresh=True)

        assert [item.title for item in results] == ["B", "C", "A"]
        assert len(results) == 3

    asyncio.run(scenario())


def test_trending_service_cache_reuse():
    async def scenario() -> None:
        fetch_calls = 0

        class CountingSource(StubSource):
            async def fetch(self, limit: int) -> list[TrendingItem]:
                nonlocal fetch_calls
                fetch_calls += 1
                return await super().fetch(limit)

        source = CountingSource(
            "counter",
            [TrendingItem(title="A", url="https://a", source="counter", score=1)],
        )
        service = TrendingService([source], default_limit=1, refresh_interval_seconds=60)

        await service.fetch_trending(limit=1, force_refresh=True)
        await service.fetch_trending(limit=1)

        assert fetch_calls == 1

    asyncio.run(scenario())


def test_trending_service_records_health_and_snapshot_metadata():
    async def scenario() -> None:
        healthy_source = StubSource(
            "healthy",
            [
                TrendingItem(
                    title="Healthy Item",
                    url="https://healthy",
                    source="healthy",
                    score=5,
                    metadata={"category": "tech"},
                )
            ],
        )

        class ErrorSource(StubSource):
            async def fetch(self, limit: int) -> list[TrendingItem]:  # type: ignore[override]
                raise RuntimeError("boom")

        failing_source = ErrorSource(
            "failing",
            [
                TrendingItem(
                    title="Should Not Appear",
                    url="https://fail",
                    source="failing",
                    score=99,
                )
            ],
        )

        service = TrendingService(
            [healthy_source, failing_source],
            default_limit=2,
            refresh_interval_seconds=120,
        )

        results = await service.fetch_trending(limit=2, force_refresh=True)

        assert [item.title for item in results] == ["Healthy Item"]
        assert results[0].metadata["category"] == "tech"
        assert results[0].metadata["raw_score"] == 5

        health = await service.get_source_health()
        status_by_source = {entry.source: entry.status for entry in health}
        assert status_by_source["healthy"] == "ok"
        assert status_by_source["failing"] == "error"

        snapshot = service.snapshot()
        assert snapshot["default_limit"] == 2
        assert 2 in snapshot["cached_limits"]
        assert snapshot["last_refresh_at"] is not None
        assert any(
            source["source"] == "failing" and source["status"] == "error"
            for source in snapshot["sources"]
        )

    asyncio.run(scenario())

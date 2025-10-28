"""Hacker News front page adapter."""
from __future__ import annotations

from typing import Any

import httpx

from ..models import TrendingItem
from .base import TrendingSource


class HackerNewsTrendingSource(TrendingSource):
    name = "hackernews"
    weight = 1.0

    def __init__(self, timeout: float) -> None:
        self._timeout = timeout

    async def fetch(self, limit: int) -> list[TrendingItem]:
        params = {"tags": "front_page", "hitsPerPage": limit}
        url = "https://hn.algolia.com/api/v1/search"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        items: list[TrendingItem] = []
        for hit in data.get("hits", [])[:limit]:
            title = hit.get("title") or hit.get("story_title")
            url_value = hit.get("url") or hit.get("story_url")
            score = float(hit.get("points") or 0)
            if not title or not url_value:
                continue
            items.append(
                TrendingItem(
                    title=title,
                    url=url_value,
                    source=self.name,
                    score=score,
                    metadata={
                        "author": hit.get("author"),
                        "comments": hit.get("num_comments"),
                    },
                )
            )
        return items

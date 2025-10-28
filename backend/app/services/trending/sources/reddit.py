"""Reddit adapter for popular posts."""
from __future__ import annotations

from typing import Any

import httpx

from ..models import TrendingItem
from .base import TrendingSource


class RedditTrendingSource(TrendingSource):
    name = "reddit"
    weight = 1.1

    def __init__(self, timeout: float) -> None:
        self._timeout = timeout

    async def fetch(self, limit: int) -> list[TrendingItem]:
        headers = {"User-Agent": "AutonomousTrendBot/0.1"}
        params = {"limit": limit}
        url = "https://www.reddit.com/r/popular.json"
        async with httpx.AsyncClient(timeout=self._timeout, headers=headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        items: list[TrendingItem] = []
        for entry in data.get("data", {}).get("children", []):
            post: dict[str, Any] = entry.get("data", {})
            title = post.get("title")
            permalink = post.get("permalink")
            score = float(post.get("score") or 0)
            if not title or not permalink:
                continue
            url = f"https://www.reddit.com{permalink}"
            items.append(
                TrendingItem(
                    title=title,
                    url=url,
                    source=self.name,
                    score=score,
                    metadata={
                        "subreddit": post.get("subreddit"),
                        "comments": post.get("num_comments"),
                    },
                )
            )
        return items

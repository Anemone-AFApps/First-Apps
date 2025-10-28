"""GitHub trending repositories adapter."""
from __future__ import annotations

from typing import Any

import httpx

from ..models import TrendingItem
from .base import TrendingSource


class GitHubTrendingSource(TrendingSource):
    name = "github"
    weight = 1.2

    def __init__(self, timeout: float) -> None:
        self._timeout = timeout

    async def fetch(self, limit: int) -> list[TrendingItem]:
        params = {"q": "stars:>1", "sort": "stars", "order": "desc", "per_page": limit}
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "AutonomousTrendBot/0.1",
        }
        url = "https://api.github.com/search/repositories"
        async with httpx.AsyncClient(timeout=self._timeout, headers=headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        items: list[TrendingItem] = []
        for repo in data.get("items", [])[:limit]:
            name = repo.get("full_name")
            html_url = repo.get("html_url")
            score = float(repo.get("stargazers_count") or 0)
            if not name or not html_url:
                continue
            items.append(
                TrendingItem(
                    title=name,
                    url=html_url,
                    source=self.name,
                    score=score,
                    metadata={
                        "description": repo.get("description"),
                        "language": repo.get("language"),
                        "stars": repo.get("stargazers_count"),
                    },
                )
            )
        return items

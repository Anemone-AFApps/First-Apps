"""Self-healing automation stubs.

This module defines the entry points for background monitors that keep the
platform in a healthy state. Each monitor can be scheduled to run on a timer
or react to events emitted by the core API.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class HealableComponent(Protocol):
    """Interface for subsystems that support automated remediation."""

    name: str

    async def diagnose(self) -> dict[str, str]:
        """Return diagnostics used to detect failure conditions."""

    async def heal(self, *, reason: str) -> None:
        """Attempt to restore the subsystem after a failure."""


@dataclass(slots=True)
class MonitorResult:
    component: str
    status: str
    details: dict[str, str]


async def run_health_cycle(component: HealableComponent) -> MonitorResult:
    """Execute a single health-check and healing attempt for a component."""
    diagnostics = await component.diagnose()
    status = diagnostics.get("status", "unknown")

    if status != "healthy":
        await component.heal(reason=diagnostics.get("reason", "unspecified"))
        status = "healing"

    return MonitorResult(component=component.name, status=status, details=diagnostics)


@dataclass(slots=True)
class TrendingServiceMonitor:
    """Basic implementation that keeps the trending aggregation responsive."""

    service: TrendingService
    name: str = "trending_service"

    async def diagnose(self) -> dict[str, str]:
        snapshot = self.service.snapshot()
        failing = [s for s in snapshot["sources"] if s.get("status") == "error"]
        status = "healthy" if not failing else "degraded"
        reason = ", ".join(s.get("source", "unknown") for s in failing) if failing else ""
        return {
            "status": status,
            "reason": reason or "operational",
        }

    async def heal(self, *, reason: str) -> None:
        await self.service.fetch_trending(force_refresh=True)

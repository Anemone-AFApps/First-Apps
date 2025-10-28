"""Test configuration and path bootstrap for backend unit tests."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repository root is available on ``sys.path`` so that tests can
# import the ``backend`` package without requiring an editable installation.
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import asyncio
import inspect
from collections.abc import Awaitable, Callable

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers used across the backend test-suite."""
    config.addinivalue_line(
        "markers",
        "asyncio: mark a test function as requiring an event loop",
    )


def _run_coroutine(coro: Awaitable[object]) -> object:
    """Run the provided coroutine in a fresh event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    """Execute ``async def`` tests marked with ``@pytest.mark.asyncio``."""
    test_function: Callable[..., object] = pyfuncitem.obj

    if not inspect.iscoroutinefunction(test_function):
        return None

    if pyfuncitem.get_closest_marker("asyncio") is None:
        raise RuntimeError(
            "Async test functions must be marked with @pytest.mark.asyncio"
        )

    coro = test_function(**pyfuncitem.funcargs)
    _run_coroutine(coro)
    return True

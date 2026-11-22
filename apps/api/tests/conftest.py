"""Shared test setup: pytest loads this file automatically before the tests."""

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

# Fake database settings so the app can be imported without a real .env.
# They must be set BEFORE importing the app, which reads them at import time.
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")

from app.core.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from tests.fakes import FakeSession  # noqa: E402


@pytest.fixture
def client() -> Iterator[TestClient]:
    """An HTTP client that calls the app directly, without a real server."""
    with TestClient(app) as test_client:
        yield test_client
    # Undo any dependency override so it cannot leak into the next test
    app.dependency_overrides.clear()


@pytest.fixture
def fake_db() -> FakeSession:
    """Replace the real database session with a fake one for this test."""
    session = FakeSession()
    app.dependency_overrides[get_db] = lambda: session
    return session

"""Shared test setup: pytest loads this file automatically before the tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.main import app
from app.models import Base
from tests.fakes import FakeSession

settings = get_settings()
TEST_DB_NAME = f"{settings.postgres_db}_test"
TEST_DATABASE_URL = settings.model_copy(update={"postgres_db": TEST_DB_NAME}).database_url
# The "postgres" database always exists: we connect to it to create the test database
ADMIN_DATABASE_URL = settings.model_copy(update={"postgres_db": "postgres"}).database_url


@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    """Create a fresh test database once for the whole test run."""
    admin_engine = create_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        exists = connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": TEST_DB_NAME},
        )
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(engine)  # start from empty tables
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Iterator[Session]:
    """A database session whose changes are rolled back after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    # "create_savepoint": session.commit() in our code only commits a savepoint,
    # so the outer transaction can still undo everything at the end of the test
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


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


@pytest.fixture
def db(db_session: Session) -> Session:
    """Make the routes use the test database session for this test."""
    app.dependency_overrides[get_db] = lambda: db_session
    return db_session

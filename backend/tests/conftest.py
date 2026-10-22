"""Pytest fixtures for unit tests (SQLite in-memory) and real PostgreSQL integration tests."""

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.models import Base

# ==============================================================================
# SQLite In-Memory Fixtures for Unit Testing
# ==============================================================================


@pytest.fixture(scope="session")
def sqlite_engine():
    """Create a persistent in-memory SQLite engine for the test session with FK enforcement."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Attach foreign key pragma listener ONLY to this SQLite engine
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(sqlite_engine) -> Generator[Session, None, None]:
    """Provide a transactional SQLite session that cleanly rolls back after each test."""
    connection = sqlite_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


# ==============================================================================
# Real PostgreSQL Integration Fixtures (documentai_thesis_test)
# ==============================================================================


@pytest.fixture(scope="session")
def pg_engine():
    """Create a connection engine to the isolated local PostgreSQL test database.

    Skips tests gracefully if local PostgreSQL test database is unreachable.
    """
    settings = get_settings()
    engine = create_engine(
        settings.sqlalchemy_test_database_uri,
        pool_pre_ping=True,
    )
    try:
        with engine.begin() as conn:
            conn.execute(text("SELECT 1;"))
    except Exception as exc:
        pytest.skip(f"PostgreSQL test database not available: {exc}")

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def pg_session(pg_engine) -> Generator[Session, None, None]:
    """Provide an isolated database session on the real PostgreSQL test database."""
    connection = pg_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()

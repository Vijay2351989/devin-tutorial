"""
Shared pytest fixtures.

Every test gets a fresh in-memory SQLite database so tests never touch the
``products.db`` file used in development.
"""

from typing import AsyncIterator, Iterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app import database
from app.database import get_db, init_db
from app.main import app
from app.models import Base

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def test_engine() -> Iterator[Engine]:
    """Provide an initialised in-memory SQLite engine."""
    engine = database.create_db_engine(TEST_DATABASE_URL)
    init_db(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Iterator[Session]:
    """Provide a session bound to the in-memory test engine."""
    factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
async def client(test_engine: Engine) -> AsyncIterator[AsyncClient]:
    """HTTP client for the app with ``get_db`` overridden to the test engine."""
    factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    def override_get_db() -> Iterator[Session]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

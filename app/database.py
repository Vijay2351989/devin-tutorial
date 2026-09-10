"""
Database configuration and session management.

The connection string is read from the ``DATABASE_URL`` environment variable
and defaults to a local SQLite file (``sqlite:///./products.db``).
"""

import logging
import os
from typing import Generator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_DATABASE_URL = "sqlite:///./products.db"
SCHEMA_VERSION = 1


def get_database_url() -> str:
    """Return the configured database URL, falling back to the SQLite default."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def create_db_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine with SQLite-appropriate pooling settings."""
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        if ":memory:" in database_url or database_url == "sqlite://":
            return create_engine(
                database_url, connect_args=connect_args, poolclass=StaticPool
            )
        return create_engine(database_url, connect_args=connect_args)
    return create_engine(database_url, pool_pre_ping=True)


engine: Engine = create_db_engine(get_database_url())
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def configure_engine(database_url: str) -> Engine:
    """Rebind the module-level engine and session factory to a new URL."""
    global engine
    engine = create_db_engine(database_url)
    SessionLocal.configure(bind=engine)
    return engine


def init_db(db_engine: Optional[Engine] = None) -> None:
    """Create all tables and record the schema version if they do not exist."""
    target = db_engine if db_engine is not None else engine
    Base.metadata.create_all(bind=target)
    with target.begin() as conn:
        conn.execute(
            text("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)")
        )
        current = conn.execute(text("SELECT MAX(version) FROM schema_version"))
        if current.scalar() is None:
            conn.execute(
                text("INSERT INTO schema_version (version) VALUES (:v)"),
                {"v": SCHEMA_VERSION},
            )
    logger.info("Database initialised (schema version %s)", SCHEMA_VERSION)


def get_schema_version(db_engine: Optional[Engine] = None) -> int:
    """Return the schema version stored in the database (0 if uninitialised)."""
    target = db_engine if db_engine is not None else engine
    with target.connect() as conn:
        try:
            result = conn.execute(text("SELECT MAX(version) FROM schema_version"))
        except Exception:
            return 0
        value = result.scalar()
        return int(value) if value is not None else 0


def check_connection(db_engine: Optional[Engine] = None) -> bool:
    """Return True if a trivial query can be executed against the database."""
    target = db_engine if db_engine is not None else engine
    try:
        with target.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("Database connection failed: %s", type(exc).__name__)
        return False


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session that is always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

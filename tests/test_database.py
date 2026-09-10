"""
Tests for database configuration, initialisation and the Product model.
"""

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import database
from app.database import (
    DEFAULT_DATABASE_URL,
    SCHEMA_VERSION,
    check_connection,
    create_db_engine,
    get_database_url,
    get_db,
    get_schema_version,
    init_db,
)
from app.models import Product


def test_get_database_url_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """The SQLite default is used when DATABASE_URL is not set."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert get_database_url() == DEFAULT_DATABASE_URL


def test_get_database_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """DATABASE_URL overrides the default."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./other.db")
    assert get_database_url() == "sqlite:///./other.db"


def test_connection_can_be_established(test_engine: Engine) -> None:
    """A trivial query succeeds against the configured engine."""
    assert check_connection(test_engine) is True


def test_connection_failure_is_reported() -> None:
    """An unreachable database returns False instead of raising."""
    bad_engine = create_db_engine("sqlite:////nonexistent-dir/x/y/z.db")
    assert check_connection(bad_engine) is False


def test_init_db_creates_products_table(test_engine: Engine) -> None:
    """init_db creates the products table and records the schema version."""
    inspector = inspect(test_engine)
    assert "products" in inspector.get_table_names()
    columns = {c["name"]: c for c in inspector.get_columns("products")}
    assert set(columns) == {
        "id",
        "name",
        "description",
        "price",
        "created_at",
        "updated_at",
    }
    assert columns["name"]["nullable"] is False
    assert columns["price"]["nullable"] is False
    assert columns["description"]["nullable"] is True
    assert columns["updated_at"]["nullable"] is True
    assert get_schema_version(test_engine) == SCHEMA_VERSION


def test_init_db_is_idempotent(test_engine: Engine) -> None:
    """Calling init_db twice does not fail or duplicate the schema version."""
    init_db(test_engine)
    init_db(test_engine)
    assert get_schema_version(test_engine) == SCHEMA_VERSION


def test_schema_version_zero_on_fresh_database() -> None:
    """A database without the schema_version table reports version 0."""
    engine = create_db_engine("sqlite:///:memory:")
    assert get_schema_version(engine) == 0


def test_product_crud(db_session: Session) -> None:
    """Products can be created, read, updated and deleted."""
    product = Product(name="Widget", description="A widget", price=9.99)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    assert product.id is not None
    assert product.created_at is not None
    assert product.updated_at is None
    assert "Widget" in repr(product)

    fetched = db_session.execute(
        select(Product).where(Product.id == product.id)
    ).scalar_one()
    assert fetched.name == "Widget"
    assert fetched.price == 9.99

    fetched.price = 19.99
    db_session.commit()
    db_session.refresh(fetched)
    assert fetched.price == 19.99
    assert fetched.updated_at is not None

    db_session.delete(fetched)
    db_session.commit()
    assert db_session.execute(select(Product)).scalars().all() == []


def test_product_name_is_required(db_session: Session) -> None:
    """Inserting a product without a name violates the NOT NULL constraint."""
    db_session.add(Product(price=1.0))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_product_price_must_be_non_negative(db_session: Session) -> None:
    """Inserting a negative price violates the check constraint."""
    db_session.add(Product(name="Bad", price=-1.0))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_get_db_yields_and_closes_session() -> None:
    """The get_db dependency yields a usable session bound to the engine."""
    engine = database.configure_engine("sqlite:///:memory:")
    init_db(engine)
    generator = get_db()
    session = next(generator)
    assert isinstance(session, Session)
    assert session.get_bind() is engine
    with pytest.raises(StopIteration):
        next(generator)

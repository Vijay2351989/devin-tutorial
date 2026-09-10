"""
Tests for the POST /api/products endpoint.
"""

from typing import Iterator

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import create_db_engine, get_db
from app.main import app
from app.models import Product
from app.schemas import ProductCreate, ProductResponse


@pytest.mark.asyncio
async def test_create_product_success(client: AsyncClient, test_engine: Engine) -> None:
    """A valid payload returns 201 with the stored product."""
    payload = {"name": "Widget", "description": "A useful widget", "price": 9.99}
    response = await client.post("/api/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Widget"
    assert data["description"] == "A useful widget"
    assert data["price"] == 9.99
    assert data["created_at"] is not None
    assert data["updated_at"] is None

    with Session(test_engine) as session:
        stored = session.execute(select(Product)).scalar_one()
        assert stored.name == "Widget"


@pytest.mark.asyncio
async def test_create_product_without_description(client: AsyncClient) -> None:
    """Description is optional and duplicates names are allowed."""
    first = await client.post("/api/products", json={"name": "Gadget", "price": 0})
    second = await client.post("/api/products", json={"name": "Gadget", "price": 1})
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["description"] is None
    assert first.json()["id"] != second.json()["id"]


@pytest.mark.asyncio
async def test_create_product_missing_name(client: AsyncClient) -> None:
    """A missing name is rejected with 422."""
    response = await client.post("/api/products", json={"price": 5.0})
    assert response.status_code == 422
    assert any(err["loc"][-1] == "name" for err in response.json()["detail"])


@pytest.mark.asyncio
async def test_create_product_empty_name(client: AsyncClient) -> None:
    """An empty name is rejected with 422."""
    response = await client.post("/api/products", json={"name": "", "price": 5.0})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_product_name_too_long(client: AsyncClient) -> None:
    """A name longer than 255 characters is rejected with 422."""
    response = await client.post(
        "/api/products", json={"name": "x" * 256, "price": 5.0}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_product_negative_price(client: AsyncClient) -> None:
    """A negative price is rejected with 422."""
    response = await client.post("/api/products", json={"name": "Bad", "price": -1})
    assert response.status_code == 422
    assert any(err["loc"][-1] == "price" for err in response.json()["detail"])


@pytest.mark.asyncio
async def test_create_product_invalid_price_type(client: AsyncClient) -> None:
    """A non-numeric price is rejected with 422."""
    response = await client.post("/api/products", json={"name": "Bad", "price": "free"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_product_database_error(client: AsyncClient) -> None:
    """Database failures (here: missing table) return 500 with a generic body."""
    factory = sessionmaker(bind=create_db_engine("sqlite:///:memory:"))

    def broken_db() -> Iterator[Session]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = broken_db
    try:
        response = await client.post(
            "/api/products", json={"name": "Widget", "price": 1.0}
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to save product to the database."}


def test_product_create_schema_validation() -> None:
    """ProductCreate enforces name length and non-negative price."""
    assert ProductCreate(name="ok", price=0).description is None
    with pytest.raises(ValueError):
        ProductCreate(name="ok", price=-0.01)
    with pytest.raises(ValueError):
        ProductCreate(name="", price=1)


def test_product_response_from_orm(test_engine: Engine) -> None:
    """ProductResponse can be built from an ORM instance."""
    with Session(test_engine) as session:
        product = Product(name="Widget", price=2.5)
        session.add(product)
        session.commit()
        session.refresh(product)
        response = ProductResponse.model_validate(product)
    assert response.id == product.id
    assert response.price == 2.5


@pytest.mark.asyncio
async def test_products_endpoint_in_openapi(client: AsyncClient) -> None:
    """The endpoint is documented in the OpenAPI schema used by Swagger UI."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    post = response.json()["paths"]["/api/products"]["post"]
    assert "201" in post["responses"]
    assert "422" in post["responses"]
    assert "500" in post["responses"]

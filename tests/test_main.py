"""
Tests for FastAPI Hello World Application
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    """Test the root endpoint returns hello world message."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Hello World from FastAPI!" in data["message"]
        assert "environment" in data
        assert "api_key_status" in data


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Test the health check endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "fastapi-example"


@pytest.mark.asyncio
async def test_read_item() -> None:
    """Test the read item endpoint with path parameters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/items/42")
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 42
        assert data["q"] is None


@pytest.mark.asyncio
async def test_read_item_with_query() -> None:
    """Test the read item endpoint with query parameters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/items/42?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 42
        assert data["q"] == "test"


@pytest.mark.asyncio
async def test_secrets_status() -> None:
    """Test the secrets status endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/secrets-status")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "organization_secrets" in data
        assert "API_KEY" in data["organization_secrets"]
        assert "DATABASE_URL" in data["organization_secrets"]
        assert "environment" in data

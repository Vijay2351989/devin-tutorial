"""
FastAPI Hello World Application
A basic example demonstrating FastAPI setup with environment variable support.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.models import Product
from app.schemas import ErrorResponse, ProductCreate, ProductResponse

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialise the database schema on application startup."""
    init_db()
    yield


app = FastAPI(
    title="FastAPI Example",
    description="A basic FastAPI example project",
    version="0.1.0",
    lifespan=lifespan,
)


class MessageResponse(BaseModel):
    """Response model for message endpoints."""

    message: str
    environment: Optional[str] = None
    api_key_status: Optional[str] = None


@app.get("/")
async def root() -> MessageResponse:
    """Root endpoint returning a welcome message with API key status."""
    api_key = os.getenv("API_KEY")

    # Show masked status of API key for security
    if api_key:
        api_key_status = f"configured (length: {len(api_key)})"
    else:
        api_key_status = "not configured"

    return MessageResponse(
        message="Hello World from FastAPI!",
        environment=os.getenv("ENVIRONMENT", "development"),
        api_key_status=api_key_status,
    )


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "fastapi-example"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None) -> dict:
    """Example endpoint with path parameters and query parameters."""
    return {"item_id": item_id, "q": q}


@app.get("/secrets-status")
async def secrets_status() -> dict:
    """Endpoint showing organization secret status."""
    api_key = os.getenv("API_KEY")
    database_url = os.getenv("DATABASE_URL")

    return {
        "service": "fastapi-example",
        "organization_secrets": {
            "API_KEY": {
                "status": "configured" if api_key else "not configured",
                "length": len(api_key) if api_key else 0,
                "source": "organization blueprint" if api_key else "missing",
            },
            "DATABASE_URL": {
                "status": "configured" if database_url else "not configured",
                "length": len(database_url) if database_url else 0,
                "source": "organization blueprint" if database_url else "missing",
            },
        },
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@app.post(
    "/api/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"description": "Validation error (missing name, negative price, ...)"},
        500: {"model": ErrorResponse, "description": "Database failure"},
    },
    tags=["products"],
)
async def create_product(
    payload: ProductCreate, db: Session = Depends(get_db)
) -> ProductResponse:
    """Create a product and persist it to the database.

    Args:
        payload: ``ProductCreate`` body with ``name`` (required, <=255 chars),
            optional ``description`` and ``price`` (required, >= 0).
        db: Database session injected by ``get_db``.

    Returns:
        The stored product including its generated ``id`` and timestamps.

    Raises:
        HTTPException: 500 when the database operation fails. Request
            validation errors are returned by FastAPI as 422.
    """
    product = Product(
        name=payload.name, description=payload.description, price=payload.price
    )
    try:
        db.add(product)
        db.commit()
        db.refresh(product)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to create product: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save product to the database.",
        ) from exc
    return ProductResponse.model_validate(product)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

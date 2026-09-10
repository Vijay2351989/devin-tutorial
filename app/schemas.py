"""
Pydantic request/response models for the products API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """Request body for creating a product."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Widget",
                    "description": "A useful widget",
                    "price": 9.99,
                }
            ]
        }
    )

    name: str = Field(
        ..., min_length=1, max_length=255, description="Product name (1-255 chars)."
    )
    description: Optional[str] = Field(
        default=None, description="Optional product description."
    )
    price: float = Field(
        ..., ge=0, strict=True, description="Non-negative numeric product price."
    )


class ProductResponse(BaseModel):
    """A product as returned by the API."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Widget",
                    "description": "A useful widget",
                    "price": 9.99,
                    "created_at": "2024-01-01T12:00:00",
                    "updated_at": None,
                }
            ]
        },
    )

    id: int = Field(..., description="Generated product identifier.")
    name: str = Field(..., description="Product name.")
    description: Optional[str] = Field(default=None, description="Description.")
    price: float = Field(..., description="Product price.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")
    updated_at: Optional[datetime] = Field(
        default=None, description="Last update timestamp (UTC), if any."
    )


class ErrorResponse(BaseModel):
    """Standard error body."""

    detail: str = Field(..., description="Human-readable error message.")

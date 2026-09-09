"""
FastAPI Hello World Application
A basic example demonstrating FastAPI setup with environment variable support.
"""

import os
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="FastAPI Example",
    description="A basic FastAPI example project",
    version="0.1.0"
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
        api_key_status=api_key_status
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
                "source": "organization blueprint" if api_key else "missing"
            },
            "DATABASE_URL": {
                "status": "configured" if database_url else "not configured",
                "length": len(database_url) if database_url else 0,
                "source": "organization blueprint" if database_url else "missing"
            }
        },
        "environment": os.getenv("ENVIRONMENT", "development")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

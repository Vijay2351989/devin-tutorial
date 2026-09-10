"""
SQLAlchemy ORM models.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, Float, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


class Product(Base):
    """A product stored in the ``products`` table.

    Attributes:
        id: Auto-incrementing integer primary key.
        name: Product name, required, at most 255 characters.
        description: Optional free-text description.
        price: Non-negative price, required.
        created_at: Timestamp set by the database when the row is inserted.
        updated_at: Timestamp set by the database when the row is updated.
    """

    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, onupdate=func.now()
    )

    def __repr__(self) -> str:
        """Return a concise developer-facing representation."""
        return f"Product(id={self.id!r}, name={self.name!r}, price={self.price!r})"

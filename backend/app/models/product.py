"""Product catalog domain model with reference weights and HS codes."""

from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    """Product catalog item for SKU referencing, unit weights, and pricing baselines."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    hs_code: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    unit: Mapped[str] = mapped_column(String(20), default="PCS", nullable=False)
    unit_price_reference: Mapped[Decimal | None] = mapped_column(Numeric(15, 4), nullable=True)
    reference_gross_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    reference_net_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

    def __repr__(self) -> str:
        return f"<Product id={self.id} sku={self.sku!r} name={self.name!r}>"

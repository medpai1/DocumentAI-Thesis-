"""Shipment and ShipmentItem domain models for export logistics execution."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.order import Order, OrderItem
    from app.models.product import Product


class Shipment(Base, TimestampMixin):
    """Physical shipment execution entity grouping documents and packaged goods."""

    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shipment_number: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )  # draft, in_preparation, documents_uploaded, review_required, ready_for_declaration, closed

    origin_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    destination_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    port_of_loading: Mapped[str | None] = mapped_column(String(100), nullable=True)
    port_of_discharge: Mapped[str | None] = mapped_column(String(100), nullable=True)
    carrier_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    booking_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vessel_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    voyage_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    etd: Mapped[date | None] = mapped_column(Date, nullable=True)
    eta: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    order: Mapped["Order | None"] = relationship(back_populates="shipments")
    items: Mapped[list["ShipmentItem"]] = relationship(
        back_populates="shipment",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="shipment",
        cascade="all, delete-orphan",
        order_by="Document.id",
    )

    def __repr__(self) -> str:
        return f"<Shipment id={self.id} number={self.shipment_number!r} status={self.status!r}>"


class ShipmentItem(Base, TimestampMixin):
    """Packed cargo line item belonging to a physical shipment."""

    __tablename__ = "shipment_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("order_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="PCS", nullable=False)
    package_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    package_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # CARTON, PALLET, DRUM
    gross_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    net_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

    # Relationships
    shipment: Mapped["Shipment"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()
    order_item: Mapped["OrderItem | None"] = relationship()

    def __repr__(self) -> str:
        return f"<ShipmentItem id={self.id} shipment_id={self.shipment_id} qty={self.quantity}>"

"""Party domain model representing trade participants."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Party(Base, TimestampMixin):
    """Trade partner entity representing buyers, sellers, shippers, and consignees."""

    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    party_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # buyer, seller, shipper, consignee
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<Party id={self.id} name={self.name!r} type={self.party_type!r}>"

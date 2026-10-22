"""Document and DocumentVersion domain models preserving historical immutability."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.shipment import Shipment
    from app.models.user import User


class Document(Base, TimestampMixin):
    """Logical document entity representing an export trade document in a shipment workflow.

    Maintains overall document state (e.g., uploaded, review_required, approved)
    and references the active/current immutable version without overwriting history.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # commercial_invoice, packing_list, bill_of_lading, other
    document_number: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",
        nullable=False,
    )  # uploaded, queued, processing, review_required, approved, rejected
    current_version_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Relationships
    shipment: Mapped["Shipment"] = relationship(back_populates="documents")
    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.version_number",
        foreign_keys="DocumentVersion.document_id",
    )

    def __repr__(self) -> str:
        return (
            f"<Document id={self.id} type={self.document_type!r} "
            f"number={self.document_number!r} status={self.status!r}>"
        )


class DocumentVersion(Base):
    """Immutable physical file revision of a logical document.

    Once created, a DocumentVersion record is never updated or overwritten.
    Any re-upload or document revision creates a new version record with an
    incremented version_number. Original binary files are stored on disk.
    """

    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_document_version_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )  # Relative disk path or object storage key
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Original upload name
    file_hash_sha256: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )  # SHA-256 hex digest
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf", nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    # Notice: DocumentVersion has NO updated_at because historical file revisions are immutable.

    # Relationships
    document: Mapped["Document"] = relationship(
        back_populates="versions",
        foreign_keys=[document_id],
    )
    uploaded_by: Mapped["User | None"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<DocumentVersion id={self.id} doc_id={self.document_id} "
            f"v={self.version_number} sha={self.file_hash_sha256[:8]}>"
        )

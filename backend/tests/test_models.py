"""Unit tests for domain models, constraints, and relationships (using SQLite in-memory)."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    Document,
    DocumentVersion,
    Order,
    OrderItem,
    Party,
    Product,
    Shipment,
    ShipmentItem,
    User,
)


def test_user_creation_and_defaults(db_session):
    """Test User entity attributes, default active status, and string representation."""
    user = User(
        email="operator@example.com",
        hashed_password="secure_hashed_password_123",
        full_name="Nguyen Van A",
        role="operator",
    )
    db_session.add(user)
    db_session.flush()

    assert user.id is not None
    assert user.is_active is True
    assert user.role == "operator"
    assert "<User" in repr(user)


def test_party_and_product_numeric_precision(db_session):
    """Test Party and Product models, asserting exact Decimal numeric representations."""
    party = Party(
        name="Vinatrade Export Corp",
        code="VINA-EXP",
        party_type="seller",
        tax_id="0101234567",
        country="Vietnam",
    )
    product = Product(
        sku="CASHEW-W240",
        name="Cashew Kernels W240",
        hs_code="08013200",
        unit="KG",
        unit_price_reference=Decimal("7.8500"),
        reference_gross_weight=Decimal("20.5000"),
        reference_net_weight=Decimal("20.0000"),
    )
    db_session.add_all([party, product])
    db_session.flush()

    assert party.id is not None
    assert product.id is not None
    assert isinstance(product.unit_price_reference, Decimal)
    assert product.unit_price_reference == Decimal("7.8500")
    assert product.reference_gross_weight == Decimal("20.5000")


def test_order_and_items_relationship_and_cascade(db_session):
    """Test Order creation with line items and cascade deletion on order deletion."""
    buyer = Party(name="Global Food Importers Ltd", party_type="buyer")
    seller = Party(name="Saigon Agro Export", party_type="seller")
    product = Product(sku="RICE-JASMINE-5P", name="Jasmine Rice 5% Broken", unit="MT")
    db_session.add_all([buyer, seller, product])
    db_session.flush()

    order = Order(
        order_number="ORD-2026-001",
        buyer_id=buyer.id,
        seller_id=seller.id,
        currency="USD",
        incoterm="FOB",
        order_date=date(2026, 10, 20),
    )
    # Using relationship collection append (without redundant order=order assignment)
    item1 = OrderItem(
        product=product,
        line_number=1,
        quantity=Decimal("50.0000"),
        unit="MT",
        unit_price=Decimal("620.0000"),
        line_total=Decimal("31000.0000"),
    )
    order.items.append(item1)
    db_session.add(order)
    db_session.flush()

    order_id = order.id
    assert len(order.items) == 1
    assert order.items[0].line_total == Decimal("31000.0000")

    # Verify cascade deletion: deleting the order must automatically delete order items
    db_session.delete(order)
    db_session.flush()

    remaining_items = db_session.query(OrderItem).filter_by(order_id=order_id).all()
    assert len(remaining_items) == 0


def test_shipment_with_items_and_documents(db_session):
    """Test Shipment grouping packed cargo items and linked documents."""
    buyer = Party(name="European Importers BV", party_type="buyer")
    seller = Party(name="Danang Spices Co", party_type="seller")
    product = Product(sku="PEPPER-BLACK-500", name="Black Pepper 500g/l", unit="KG")
    db_session.add_all([buyer, seller, product])
    db_session.flush()

    order = Order(
        order_number="ORD-2026-002",
        buyer_id=buyer.id,
        seller_id=seller.id,
    )
    shipment = Shipment(
        shipment_number="SHP-2026-001",
        order=order,
        origin_country="Vietnam",
        destination_country="Netherlands",
        port_of_loading="Cat Lai, Ho Chi Minh",
        port_of_discharge="Rotterdam",
    )
    shipment_item = ShipmentItem(
        product=product,
        quantity=Decimal("10000.0000"),
        unit="KG",
        package_count=400,
        package_type="BAGS",
        gross_weight=Decimal("10200.0000"),
        net_weight=Decimal("10000.0000"),
    )
    shipment.items.append(shipment_item)
    db_session.add(shipment)
    db_session.flush()

    assert shipment.id is not None
    assert len(shipment.items) == 1
    assert shipment.items[0].gross_weight == Decimal("10200.0000")


def test_document_and_version_immutability(db_session):
    """Test logical Document lifecycle and immutable preservation of DocumentVersion revisions.

    Verifies:
    1. Creating a logical document with version 1.
    2. Adding version 2 when a replacement document is issued.
    3. Asserting that version 1 data is preserved verbatim and not overwritten.
    4. Asserting both versions remain linked to the document in chronological order.
    """
    shipment = Shipment(shipment_number="SHP-2026-002")
    user = User(
        email="uploader@example.com",
        hashed_password="pw",
        full_name="Uploader Test",
    )
    db_session.add_all([shipment, user])
    db_session.flush()

    # Step 1: Create logical document
    doc = Document(
        shipment_id=shipment.id,
        document_type="commercial_invoice",
        document_number="INV-2026-001",
        status="uploaded",
    )
    db_session.add(doc)
    db_session.flush()

    # Step 2: Upload Version 1
    v1_hash = "a" * 64
    v1 = DocumentVersion(
        version_number=1,
        file_storage_key="shipments/SHP-002/INV-001_v1.pdf",
        file_name="invoice_original.pdf",
        file_hash_sha256=v1_hash,
        file_size_bytes=102400,
        mime_type="application/pdf",
        uploaded_by_id=user.id,
    )
    doc.versions.append(v1)
    db_session.flush()  # Populates v1.id

    doc.current_version_id = v1.id
    db_session.flush()

    assert len(doc.versions) == 1
    assert doc.versions[0].version_number == 1
    assert doc.versions[0].file_hash_sha256 == v1_hash

    # Step 3: Upload Version 2 (Revised document issued)
    v2_hash = "b" * 64
    v2 = DocumentVersion(
        version_number=2,
        file_storage_key="shipments/SHP-002/INV-001_v2.pdf",
        file_name="invoice_amended.pdf",
        file_hash_sha256=v2_hash,
        file_size_bytes=103500,
        mime_type="application/pdf",
        uploaded_by_id=user.id,
    )
    doc.versions.append(v2)
    db_session.flush()  # Populates v2.id

    doc.current_version_id = v2.id
    doc.status = "review_required"
    db_session.flush()

    # Assert: Historical version 1 remains intact, version 2 is recorded, order is preserved
    assert len(doc.versions) == 2
    assert doc.versions[0].version_number == 1
    assert doc.versions[0].file_hash_sha256 == v1_hash
    assert doc.versions[0].file_name == "invoice_original.pdf"

    assert doc.versions[1].version_number == 2
    assert doc.versions[1].file_hash_sha256 == v2_hash
    assert doc.versions[1].file_name == "invoice_amended.pdf"
    assert doc.current_version_id == v2.id


def test_unique_constraint_enforcement(db_session):
    """Test that unique constraints are enforced on duplicate emails
    and duplicate (document_id, version_number) tuples.
    """
    # 1. Unique email on User
    u1 = User(email="unique@example.com", hashed_password="pw", full_name="User 1")
    u2 = User(email="unique@example.com", hashed_password="pw", full_name="User 2")
    db_session.add(u1)
    db_session.flush()

    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    # 2. Unique (document_id, version_number) on DocumentVersion
    shipment = Shipment(shipment_number="SHP-UNIQUE")
    db_session.add(shipment)
    db_session.flush()

    doc = Document(shipment_id=shipment.id, document_type="packing_list")
    db_session.add(doc)
    db_session.flush()

    v1_a = DocumentVersion(
        version_number=1,
        file_storage_key="key1.pdf",
        file_name="pl.pdf",
        file_hash_sha256="c" * 64,
        file_size_bytes=5000,
    )
    doc.versions.append(v1_a)
    db_session.flush()

    v1_b = DocumentVersion(
        document_id=doc.id,
        version_number=1,  # Duplicate version number for same document!
        file_storage_key="key2.pdf",
        file_name="pl_dup.pdf",
        file_hash_sha256="d" * 64,
        file_size_bytes=5000,
    )
    db_session.add(v1_b)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_foreign_key_delete_restriction(db_session):
    """Test that ondelete='RESTRICT' prevents deleting a Party referenced by an Order."""
    buyer = Party(name="Protected Buyer", party_type="buyer")
    seller = Party(name="Protected Seller", party_type="seller")
    db_session.add_all([buyer, seller])
    db_session.flush()

    order = Order(
        order_number="ORD-RESTRICT-001",
        buyer_id=buyer.id,
        seller_id=seller.id,
    )
    db_session.add(order)
    db_session.flush()

    # Attempting to delete the buyer while an order references it must raise an IntegrityError
    db_session.delete(buyer)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_session_transaction_rollback(db_session):
    """Test that uncommitted or aborted operations leave no uncommitted rows."""
    product = Product(sku="TEMP-SKU-99", name="Temporary Product", unit="PCS")
    db_session.add(product)
    db_session.flush()

    # Explicitly rollback the transaction
    db_session.rollback()

    queried = db_session.query(Product).filter_by(sku="TEMP-SKU-99").first()
    assert queried is None

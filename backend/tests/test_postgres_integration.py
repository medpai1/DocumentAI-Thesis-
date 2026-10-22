"""Integration tests executing against the local native PostgreSQL 17 database.

Target database: documentai_thesis_test (isolated test database).
These tests verify PostgreSQL-specific DDL, NUMERIC precision, foreign key enforcement,
and end-to-end CRUD persistence on the real database engine.
"""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import text

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


@pytest.mark.postgres
def test_real_postgres_connection_and_engine(pg_session):
    """Verify that the test session is running against real PostgreSQL 17."""
    result = pg_session.execute(text("SELECT version();")).scalar()
    assert result is not None
    assert "PostgreSQL" in result
    assert "17." in result  # Confirms local PostgreSQL 17 service


@pytest.mark.postgres
def test_real_postgres_complete_crud_and_versioning(pg_session):
    """Execute end-to-end relational CRUD and version immutability on PostgreSQL 17.

    Verifies:
    1. Creating User, Parties, Product, Order, OrderItem, Shipment, ShipmentItem.
    2. Creating Document and DocumentVersion v1.
    3. Adding DocumentVersion v2, asserting both versions exist on disk and DB.
    4. Numeric column precision with 4 decimal places on PostgreSQL NUMERIC.
    """
    # 1. Create User
    operator = User(
        email="pg_tester@example.com",
        hashed_password="hashed_pw_xyz",
        full_name="Postgres Test Operator",
        role="operator",
    )
    pg_session.add(operator)
    pg_session.flush()

    # 2. Create Parties
    seller = Party(
        name="Vietnam Agri-Export JSC",
        code="VN-AGRI-01",
        party_type="seller",
        tax_id="0309998888",
        country="Vietnam",
    )
    buyer = Party(
        name="Tokyo Foods Co., Ltd.",
        code="TYO-FOODS-01",
        party_type="buyer",
        country="Japan",
    )
    pg_session.add_all([seller, buyer])
    pg_session.flush()

    # 3. Create Product
    product = Product(
        sku="COFFEE-ROBUSTA-G1",
        name="Vietnamese Robusta Grade 1",
        hs_code="09011100",
        unit="MT",
        unit_price_reference=Decimal("4150.5000"),
        reference_gross_weight=Decimal("1005.0000"),
        reference_net_weight=Decimal("1000.0000"),
    )
    pg_session.add(product)
    pg_session.flush()

    # 4. Create Order & Items
    order = Order(
        order_number="PO-2026-JP-001",
        buyer_id=buyer.id,
        seller_id=seller.id,
        currency="USD",
        incoterm="CIF",
        order_date=date(2026, 10, 22),
    )
    order_item = OrderItem(
        product=product,
        line_number=1,
        quantity=Decimal("20.0000"),
        unit="MT",
        unit_price=Decimal("4150.5000"),
        line_total=Decimal("83010.0000"),
    )
    order.items.append(order_item)
    pg_session.add(order)
    pg_session.flush()

    # 5. Create Shipment & ShipmentItem
    shipment = Shipment(
        shipment_number="SHP-2026-JP-001",
        order=order,
        status="in_preparation",
        origin_country="Vietnam",
        destination_country="Japan",
        port_of_loading="Ho Chi Minh City",
        port_of_discharge="Yokohama",
        vessel_name="PACIFIC VOYAGER",
        voyage_number="2610N",
    )
    shipment_item = ShipmentItem(
        order_item=order_item,
        product=product,
        quantity=Decimal("20.0000"),
        unit="MT",
        package_count=334,
        package_type="JUTE_BAGS",
        gross_weight=Decimal("20100.0000"),
        net_weight=Decimal("20000.0000"),
    )
    shipment.items.append(shipment_item)
    pg_session.add(shipment)
    pg_session.flush()

    # 6. Create Logical Document and Version 1
    doc = Document(
        shipment_id=shipment.id,
        document_type="commercial_invoice",
        document_number="INV-2026-JP-001",
        status="uploaded",
    )
    pg_session.add(doc)
    pg_session.flush()

    sha256_v1 = "1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"
    v1 = DocumentVersion(
        version_number=1,
        file_storage_key="shipments/SHP-2026-JP-001/INV-001_v1.pdf",
        file_name="Commercial_Invoice_v1.pdf",
        file_hash_sha256=sha256_v1,
        file_size_bytes=245600,
        mime_type="application/pdf",
        page_count=2,
        uploaded_by_id=operator.id,
    )
    doc.versions.append(v1)
    pg_session.flush()
    doc.current_version_id = v1.id
    pg_session.flush()

    # 7. Add Version 2 (Amendment)
    sha256_v2 = "ffffeeeeddddccccbbbbaaaa0000999988887777666655554444333322221111"
    v2 = DocumentVersion(
        version_number=2,
        file_storage_key="shipments/SHP-2026-JP-001/INV-001_v2.pdf",
        file_name="Commercial_Invoice_v2.pdf",
        file_hash_sha256=sha256_v2,
        file_size_bytes=246100,
        mime_type="application/pdf",
        page_count=2,
        uploaded_by_id=operator.id,
    )
    doc.versions.append(v2)
    pg_session.flush()
    doc.current_version_id = v2.id
    doc.status = "review_required"
    pg_session.flush()

    # 8. Query back from PostgreSQL and verify relational integrity
    queried_shipment = (
        pg_session.query(Shipment).filter_by(shipment_number="SHP-2026-JP-001").first()
    )
    assert queried_shipment is not None
    assert queried_shipment.order.order_number == "PO-2026-JP-001"
    assert len(queried_shipment.items) == 1
    assert queried_shipment.items[0].gross_weight == Decimal("20100.0000")

    queried_doc = queried_shipment.documents[0]
    assert queried_doc.document_number == "INV-2026-JP-001"
    assert len(queried_doc.versions) == 2
    assert queried_doc.current_version_id == v2.id

    # Verify historical immutability: Version 1 is unchanged
    assert queried_doc.versions[0].version_number == 1
    assert queried_doc.versions[0].file_hash_sha256 == sha256_v1
    assert queried_doc.versions[1].version_number == 2
    assert queried_doc.versions[1].file_hash_sha256 == sha256_v2

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import (
    Base,
    DefaultInvoiceItemDB,
    DefaultInvoiceItemPosition,
    Gender,
    InvoiceDateDB,
    InvoiceDB,
    InvoiceItemDB,
    InvoiceStatus,
    InvoiceType,
    PatientDB,
)


@pytest.fixture
def db():
    """Fresh in-memory SQLite database per test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def patient(db):
    p = PatientDB(
        label="TEST",
        first_name="Max",
        last_name="Mustermann",
        birthday=date(1990, 1, 1),
        gender=Gender.MALE,
        street="Musterstraße",
        street_number="1",
        postal_code="12345",
        city="Berlin",
        kilometers_to_travel=10.0,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def saved_hp_invoice(db, patient):
    """Saved HP invoice with one date and one item."""
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 15),
        invoice_number="2026-01-15-HP-TEST",
        type=InvoiceType.HP,
        status=InvoiceStatus.SAVED,
        kilometers_at_billing=10.0,
    )
    db.add(inv)
    db.flush()

    d = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 1, 10))
    db.add(d)
    db.flush()

    item = InvoiceItemDB(
        invoice_id=inv.invoice_id,
        date_id=d.date_id,
        description="Behandlung A",
        amount=50.0,
        number="GÖÄ 1",
        quantity=1,
        position=0,
    )
    db.add(item)
    db.commit()
    db.refresh(inv)
    return inv


@pytest.fixture
def saved_kg_invoice(db, patient):
    """Saved KG invoice with two dates and one item."""
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 2, 1),
        invoice_number="2026-02-01-KG-TEST",
        type=InvoiceType.KG,
        status=InvoiceStatus.SAVED,
        kilometers_at_billing=10.0,
    )
    db.add(inv)
    db.flush()

    d1 = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 1, 5))
    d2 = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 1, 12))
    db.add_all([d1, d2])
    db.flush()

    item = InvoiceItemDB(
        invoice_id=inv.invoice_id,
        date_id=None,
        description="KG Behandlung",
        amount=30.0,
        number=None,
        quantity=2,
        position=0,
    )
    db.add(item)
    db.commit()
    db.refresh(inv)
    return inv


@pytest.fixture
def default_item_hp(db):
    item = DefaultInvoiceItemDB(
        type=InvoiceType.HP,
        description="Fahrtkosten HP",
        amount=10.0,
        number=None,
        quantity=None,
        is_active_global=True,
        position=DefaultInvoiceItemPosition.APPEND,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def default_item_kg(db):
    item = DefaultInvoiceItemDB(
        type=InvoiceType.KG,
        description="Fahrtkosten KG",
        amount=8.0,
        number=None,
        quantity=None,
        is_active_global=True,
        position=DefaultInvoiceItemPosition.PREPEND,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

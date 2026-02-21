from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session

from .invoiceItem_service import validate_invoice_item
from .patient_service import load_patient
from ..models import (
    InvoiceDB,
    InvoiceDateDB,
    InvoiceItemDB,
    PatientDB,
    InvoiceInvoiceDefaultItemAssociationDB, InvoiceStatus
)
from ..schemas import InvoiceCreate, InvoiceDateCreate
from ..utilities.database import add_db


def load_invoices(
        show_drafts: bool,
        only_drafts: bool,
        search: Optional[str],
        db: Session
) -> list[InvoiceDB]:
    statement = select(InvoiceDB)

    if only_drafts:
        statement = statement.where(InvoiceDB.is_draft.is_(True))
    elif not show_drafts:
        statement = statement.where(InvoiceDB.is_draft.is_(False))

    if search:
        statement = statement.where(
            InvoiceDB.invoice_number.ilike(f"%{search}%")
        )

    return list(db.scalars(statement).all())


def load_invoice(invoice_id: int, db: Session) -> InvoiceDB:
    statement = (
        select(InvoiceDB)
        .options(
            joinedload(InvoiceDB.patient),
            joinedload(InvoiceDB.user_items),
            joinedload(InvoiceDB.default_items),
            joinedload(InvoiceDB.dates),
        )
        .where(InvoiceDB.invoice_id == invoice_id)
    )

    invoice = db.scalars(statement).first()

    if invoice is None:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    return invoice


def create_invoice_logic(
        new_invoice: InvoiceCreate,
        db: Session,
) -> InvoiceDB:
    """
    Main entry point for creating an invoice.
    Decides by the provided type, how and which items to add.
    """
    invoice_data = new_invoice.model_dump(exclude={"user_items", "dates", "default_item_ids"})
    db_invoice = InvoiceDB(**invoice_data)
    db_invoice.status = InvoiceStatus.DRAFT

    add_db(db_invoice, db)

    patient = load_patient(new_invoice.patient_id, db)
    quantity = _process_dates(new_invoice.dates, db_invoice)

    for u_item in new_invoice.user_items:
        validate_invoice_item(u_item, new_invoice.type, quantity)
        db_invoice.user_items.append(InvoiceItemDB(**u_item.model_dump()))

    for d_id in new_invoice.default_item_ids:
        new_link = InvoiceInvoiceDefaultItemAssociationDB(
            invoice_id=db_invoice.invoice_id,
            default_item_id=d_id
        )
        db.add(new_link)

    db_invoice.kilometers_at_billing = patient.kilometers_to_travel
    db_invoice.invoice_number = _generate_unique_invoice_number(db, db_invoice, patient)

    db_invoice.status = InvoiceStatus.SAVED

    return db_invoice


def _generate_unique_invoice_number(db: Session, invoice: InvoiceDB, patient: PatientDB) -> str:
    base_number = f"{invoice.invoice_date}-{patient.label}"

    statement = select(InvoiceDB).where(
        InvoiceDB.invoice_number == base_number
    )
    exists = db.scalars(statement).first()

    if exists:
        raise HTTPException(
            status_code=409,
            detail=f"Rechnungsnummer {base_number} bereits vergeben."
        )
    return base_number


def _process_dates(
        dates: Optional[list[InvoiceDateCreate]],
        db_invoice: InvoiceDB
) -> int:
    """Adds invoice dates."""
    if not dates:
        return 1

    dates.sort(key=lambda x: x.date)

    for date_entry in dates:
        db_date = InvoiceDateDB(**date_entry.model_dump())
        db_invoice.dates.append(db_date)
    return len(dates)

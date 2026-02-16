from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session

from ..models import InvoiceDB, InvoiceDateDB, InvoiceItemDB, InvoiceType, PatientDB
from ..schemas import InvoiceCreate, InvoiceItemCreate, InvoiceDateCreate

ADDITIONAL_KG_ITEMS: list[InvoiceItemCreate] = [
    InvoiceItemCreate(description="Anamnese & Befunderhebung", quantity=1, amount=0.0),
]


def load_invoice(invoice_id: int, db: Session) -> InvoiceDB:
    invoice: Optional[InvoiceDB] = db.query(InvoiceDB).options(
        joinedload(InvoiceDB.patient),
        joinedload(InvoiceDB.items),
        joinedload(InvoiceDB.dates)
    ).filter(InvoiceDB.invoice_id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    return invoice


def create_invoice_logic(
        invoice: InvoiceCreate,
        db: Session,
) -> InvoiceDB:
    """
    Main entry point for creating an invoice.
    Decides by the provided type, how and which items to add.
    """
    invoice_data = invoice.model_dump(exclude={"items", "dates"})
    db_invoice = InvoiceDB(**invoice_data)

    patient = db.query(PatientDB).get(db_invoice.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")

    date_count = _process_dates(invoice.dates, db_invoice)

    if invoice.type == InvoiceType.KG:
        _add_kg_items(invoice.items, db_invoice, date_count)
    else:
        _add_hp_items(invoice.items, db_invoice)

    db_invoice.total = _calculate_total(db_invoice)
    db_invoice.invoice_number = _generate_unique_invoice_number(db, db_invoice, patient)
    db_invoice.is_draft = False

    return db_invoice


def _generate_unique_invoice_number(db: Session, invoice: InvoiceDB, patient: type[PatientDB]) -> str:
    base_number = f"{invoice.invoice_date}-{patient.label}"
    exists = db.query(InvoiceDB).filter(InvoiceDB.invoice_number == base_number).first()

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
        return 0

    dates.sort(key=lambda x: x.date)

    for date_entry in dates:
        db_date = InvoiceDateDB(**date_entry.model_dump())
        db_invoice.dates.append(db_date)
    return len(dates)


def _add_kg_items(
        items: list[InvoiceItemCreate],
        db_invoice: InvoiceDB,
        date_count: int
):
    """Adds fixed additional KG items and the users items."""
    for item in ADDITIONAL_KG_ITEMS:
        db_invoice.items.append(InvoiceItemDB(**item.model_dump()))

    # User Items
    for item in items:
        validate_invoice_item(item, InvoiceType.KG, date_count)
        db_invoice.items.append(InvoiceItemDB(**item.model_dump()))


def _add_hp_items(
        items: list[InvoiceItemCreate],
        db_invoice: InvoiceDB
):
    """Adds user provided items only."""
    for item in items:
        validate_invoice_item(item, InvoiceType.HP)
        db_invoice.items.append(InvoiceItemDB(**item.model_dump()))


def _calculate_total(
        db_invoice: InvoiceDB
) -> float:
    """Calculate the total of the invoice."""
    total = 0.0
    for item in db_invoice.items:
        total += (item.amount * item.quantity)
    return round(total, 2)


def validate_invoice_item(
        item: InvoiceItemCreate,
        inv_type: InvoiceType,
        quantity: int = 1
):
    """Validate and enforce item fields."""
    if item.amount < 0:
        raise HTTPException(status_code=400, detail="Betrag darf nicht negativ sein")
    if not item.description:
        raise HTTPException(status_code=400, detail="Beschreibung fehlt")

    if inv_type == InvoiceType.KG:
        item.quantity = quantity
        item.date = None
        item.number = None
    elif inv_type == InvoiceType.HP:
        if not item.number:
            raise HTTPException(status_code=400, detail="Ziffer fehlt")

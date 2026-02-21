from datetime import datetime, timezone
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
    InvoiceInvoiceDefaultItemAssociationDB, InvoiceStatus, InvoiceType
)
from ..schemas import InvoiceCreate, InvoiceDateCreate, InvoiceUpdate
from ..utilities.database import add_db


def load_invoices(
        show_drafts: bool,
        only_drafts: bool,
        search: Optional[str],
        db: Session
) -> list[InvoiceDB]:
    statement = select(InvoiceDB).options(
        joinedload(InvoiceDB.user_items),
        joinedload(InvoiceDB.dates),
        joinedload(InvoiceDB.patient),
        # Eagerly load the default items through the association table
        joinedload(InvoiceDB.default_items).joinedload(InvoiceInvoiceDefaultItemAssociationDB.default_item)
    )

    if only_drafts:
        statement = statement.where(InvoiceDB.status.is_(InvoiceStatus.DRAFT))
    elif not show_drafts:
        statement = statement.where(InvoiceDB.status.is_not(InvoiceStatus.DRAFT))

    if search:
        statement = statement.where(
            InvoiceDB.invoice_number.ilike(f"%{search}%")
        )

    return list(db.scalars(statement).unique().all())


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
    base_number = f"{invoice.invoice_date}{"-H" if invoice.type == InvoiceType.HP else ""}-{patient.label}"

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


def update_invoice_logic(
        invoice_id: int,
        invoice_update: InvoiceUpdate,
        db: Session
) -> InvoiceDB:
    # 1. Load the existing invoice
    db_invoice = load_invoice(invoice_id, db)

    # Prevent modification if the invoice is already locked
    if db_invoice.is_locked:
        raise HTTPException(status_code=403, detail="Gesperrte Rechnungen können nicht bearbeitet werden.")

    # 2. Update basic scalar fields (patient_id, invoice_date, type, diagnosis)
    # exclude_unset=True ensures we only update fields that were actually sent in the request
    update_data = invoice_update.model_dump(exclude_unset=True, exclude={"user_items", "dates", "default_item_ids"})
    for key, value in update_data.items():
        setattr(db_invoice, key, value)

    # 3. Update Many-to-Many Default Items
    if invoice_update.default_item_ids is not None:
        # Clear the existing association objects
        db_invoice.default_items.clear()

        # Create new association links based on the provided IDs
        for d_id in invoice_update.default_item_ids:
            new_link = InvoiceInvoiceDefaultItemAssociationDB(
                invoice_id=db_invoice.invoice_id,
                default_item_id=d_id
            )
            db_invoice.default_items.append(new_link)

    # 4. Update Dates (Sync logic: Update existing, Create new, Delete missing)
    if invoice_update.dates is not None:
        existing_dates = {d.date_id: d for d in db_invoice.dates}
        incoming_dates = invoice_update.dates

        # Find IDs that are kept
        incoming_ids = {d.date_id for d in incoming_dates if d.date_id is not None}

        # Remove dates that are no longer in the incoming list
        for d_id, d_obj in list(existing_dates.items()):
            if d_id not in incoming_ids:
                db_invoice.dates.remove(d_obj)

        # Update existing or add new dates
        for d_in in incoming_dates:
            if d_in.date_id and d_in.date_id in existing_dates:
                # Update existing date
                existing_dates[d_in.date_id].date = d_in.date
            else:
                # Create new date
                new_date = InvoiceDateDB(**d_in.model_dump(exclude={"date_id"}))
                db_invoice.dates.append(new_date)

    # 5. Update User Items (Sync logic)
    if invoice_update.user_items is not None:
        existing_items = {i.item_id: i for i in db_invoice.user_items}
        incoming_items = invoice_update.user_items

        # Current quantity of dates for validation
        date_count = len(db_invoice.dates) if db_invoice.dates else 1

        incoming_item_ids = {i.item_id for i in incoming_items if i.item_id is not None}

        # Remove items that are no longer in the incoming list
        for i_id, i_obj in list(existing_items.items()):
            if i_id not in incoming_item_ids:
                db_invoice.user_items.remove(i_obj)

        # Update existing or add new items
        for i_in in incoming_items:
            # Validate the item just like in creation
            validate_invoice_item(i_in, db_invoice.type, date_count)

            if i_in.item_id and i_in.item_id in existing_items:
                # Update existing item
                db_item = existing_items[i_in.item_id]
                for key, value in i_in.model_dump(exclude={"item_id"}, exclude_unset=True).items():
                    setattr(db_item, key, value)
            else:
                # Create new item
                new_item = InvoiceItemDB(**i_in.model_dump(exclude={"item_id"}))
                db_invoice.user_items.append(new_item)

    db_invoice.updated_at = datetime.now(timezone.utc)
    # Commit changes to the database
    db.commit()
    db.refresh(db_invoice)

    return db_invoice

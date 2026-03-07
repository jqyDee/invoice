from datetime import date, datetime, timezone
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
from ..schemas import InvoiceCreate, InvoiceUpdate, InvoiceDateUpdate
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
        raise HTTPException(status_code=404, detail="Rechnung konnte nicht gefunden werden.")

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
    db.flush()

    patient = load_patient(new_invoice.patient_id, db)

    if new_invoice.type == InvoiceType.HP:
        _create_hp_dates_and_items(new_invoice, db_invoice, db)
    else:
        _create_kg_dates_and_items(new_invoice, db_invoice, db)

    _link_default_items(db_invoice, new_invoice.default_item_ids, db)

    db_invoice.kilometers_at_billing = patient.kilometers_to_travel
    db_invoice.invoice_number = _generate_unique_invoice_number(db, db_invoice, patient)
    db_invoice.status = InvoiceStatus.SAVED

    return db_invoice


def _create_hp_dates_and_items(new_invoice: InvoiceCreate, db_invoice: InvoiceDB, db: Session) -> None:
    for date_schema in (new_invoice.dates or []):
        db_date = InvoiceDateDB(invoice_id=db_invoice.invoice_id, date=date_schema.date)
        db.add(db_date)
        db.flush()

        for idx, item_schema in enumerate(date_schema.items or []):
            db.add(InvoiceItemDB(
                **item_schema.model_dump(),
                invoice_id=db_invoice.invoice_id,
                date_id=db_date.date_id,
                position=idx
            ))


def _create_kg_dates_and_items(new_invoice: InvoiceCreate, db_invoice: InvoiceDB, db: Session) -> None:
    for date_schema in (new_invoice.dates or []):
        db.add(InvoiceDateDB(invoice_id=db_invoice.invoice_id, date=date_schema.date))

    for idx, item_schema in enumerate(new_invoice.user_items or []):
        db.add(InvoiceItemDB(
            **item_schema.model_dump(),
            invoice_id=db_invoice.invoice_id,
            date_id=None,
            position=idx
        ))


def _link_default_items(db_invoice: InvoiceDB, default_item_ids: list[int], db: Session) -> None:
    for d_id in default_item_ids:
        db.add(InvoiceInvoiceDefaultItemAssociationDB(
            invoice_id=db_invoice.invoice_id,
            default_item_id=d_id
        ))


def _generate_unique_invoice_number(db: Session, invoice: InvoiceDB, patient: PatientDB) -> str:
    base_number = f"{invoice.invoice_date}{'-H' if invoice.type == InvoiceType.HP else ''}-{patient.label}"

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


def update_invoice_logic(
        invoice_id: int,
        invoice_update: InvoiceUpdate,
        db: Session
) -> InvoiceDB:
    db_invoice = load_invoice(invoice_id, db)

    if db_invoice.is_locked:
        raise HTTPException(status_code=403, detail="Gesperrte Rechnungen können nicht bearbeitet werden.")

    _apply_scalar_updates(db_invoice, invoice_update)

    if invoice_update.default_item_ids is not None:
        _update_default_items(db_invoice, invoice_update.default_item_ids)

    if db_invoice.type == InvoiceType.HP:
        if invoice_update.dates is not None:
            _sync_hp_nested_structure(db_invoice, invoice_update.dates, db)
    else:
        if invoice_update.dates is not None:
            _sync_standalone_dates(db_invoice, invoice_update.dates)
        if invoice_update.user_items is not None:
            _sync_standalone_items(db_invoice, invoice_update.user_items)

    db_invoice.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def _apply_scalar_updates(db_invoice: InvoiceDB, invoice_update: InvoiceUpdate) -> None:
    update_data = invoice_update.model_dump(exclude_unset=True, exclude={"user_items", "dates", "default_item_ids"})
    for key, value in update_data.items():
        setattr(db_invoice, key, value)


def _update_default_items(db_invoice: InvoiceDB, default_item_ids: list[int]) -> None:
    db_invoice.default_items.clear()
    for d_id in default_item_ids:
        db_invoice.default_items.append(InvoiceInvoiceDefaultItemAssociationDB(
            invoice_id=db_invoice.invoice_id,
            default_item_id=d_id
        ))


def _sync_hp_nested_structure(db_invoice: InvoiceDB, incoming_dates: list[InvoiceDateUpdate], db: Session) -> None:
    """Syncs HP dates and their nested items."""
    existing_dates = {d.date_id: d for d in db_invoice.dates}
    incoming_ids = {d.date_id for d in incoming_dates if d.date_id is not None}

    # 1. Remove dates that are no longer there (cascade deletes linked items)
    for d_id, d_obj in list(existing_dates.items()):
        if d_id not in incoming_ids:
            db_invoice.dates.remove(d_obj)

    # 2. Update existing or create new dates
    for d_schema in incoming_dates:
        if d_schema.date_id in existing_dates:
            db_date = existing_dates[d_schema.date_id]
            db_date.date = d_schema.date
            _sync_items_for_date(db_invoice, db_date, d_schema.items or [], db)
        else:
            _create_hp_date_with_items(db_invoice, d_schema, db)


def _create_hp_date_with_items(db_invoice: InvoiceDB, d_schema: InvoiceDateUpdate, db: Session) -> None:
    new_date = InvoiceDateDB(invoice_id=db_invoice.invoice_id, date=d_schema.date)
    db.add(new_date)
    db.flush()

    for idx, i_schema in enumerate(d_schema.items or []):
        db.add(InvoiceItemDB(
            **i_schema.model_dump(exclude={"item_id"}),
            invoice_id=db_invoice.invoice_id,
            date_id=new_date.date_id,
            position=idx
        ))


def _sync_items_for_date(db_invoice: InvoiceDB, db_date: InvoiceDateDB, incoming_items: list, db: Session) -> None:
    """Helper to sync items linked to a specific date_id."""
    existing_items = {i.item_id: i for i in db_date.items}
    incoming_ids = {i.item_id for i in incoming_items if i.item_id is not None}

    # Delete missing items
    for i_id, i_obj in list(existing_items.items()):
        if i_id not in incoming_ids:
            db.delete(i_obj)

    # Update or Create
    db_items_in_order = []
    for i_schema in incoming_items:
        validate_invoice_item(i_schema, InvoiceType.HP, 1)
        if i_schema.item_id in existing_items:
            db_item = existing_items[i_schema.item_id]
            for key, value in i_schema.model_dump(exclude={"item_id"}, exclude_unset=True).items():
                setattr(db_item, key, value)
        else:
            db_item = InvoiceItemDB(
                **i_schema.model_dump(exclude={"item_id"}),
                invoice_id=db_invoice.invoice_id,
                date_id=db_date.date_id
            )
            db.add(db_item)
        db_items_in_order.append(db_item)

    for idx, db_item in enumerate(db_items_in_order):
        db_item.position = idx


def set_payment_due(invoice_id: int, db: Session) -> InvoiceDB:
    db_invoice = load_invoice(invoice_id, db)
    if db_invoice.is_locked:
        raise HTTPException(status_code=409, detail="Rechnung ist bereits gesperrt.")
    db_invoice.status = InvoiceStatus.PAYMENT_DUE
    db_invoice.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def set_paid(invoice_id: int, paid_at: date, db: Session) -> InvoiceDB:
    db_invoice = load_invoice(invoice_id, db)
    if db_invoice.status != InvoiceStatus.PAYMENT_DUE:
        raise HTTPException(status_code=409, detail="Rechnung muss herausgegeben sein.")
    db_invoice.status = InvoiceStatus.PAID
    db_invoice.paid_at = paid_at
    db_invoice.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def _sync_standalone_dates(db_invoice: InvoiceDB, incoming_dates: list) -> None:
    existing_dates = {d.date_id: d for d in db_invoice.dates}
    incoming_ids = {d.date_id for d in incoming_dates if d.date_id is not None}

    for d_id, d_obj in list(existing_dates.items()):
        if d_id not in incoming_ids:
            db_invoice.dates.remove(d_obj)

    for d_in in incoming_dates:
        if d_in.date_id in existing_dates:
            existing_dates[d_in.date_id].date = d_in.date
        else:
            db_invoice.dates.append(InvoiceDateDB(**d_in.model_dump(exclude={"date_id", "items"})))


def _sync_standalone_items(db_invoice: InvoiceDB, incoming_items: list) -> None:
    existing_items = {i.item_id: i for i in db_invoice.user_items if i.date_id is None}
    incoming_ids = {i.item_id for i in incoming_items if i.item_id is not None}
    date_count = len(db_invoice.dates) or 1

    for i_id, i_obj in list(existing_items.items()):
        if i_id not in incoming_ids:
            db_invoice.user_items.remove(i_obj)

    db_items_in_order = []
    for i_in in incoming_items:
        validate_invoice_item(i_in, db_invoice.type, date_count)
        if i_in.item_id in existing_items:
            db_item = existing_items[i_in.item_id]
            for key, value in i_in.model_dump(exclude={"item_id"}, exclude_unset=True).items():
                setattr(db_item, key, value)
        else:
            db_item = InvoiceItemDB(**i_in.model_dump(exclude={"item_id"}))
            db_invoice.user_items.append(db_item)
        db_items_in_order.append(db_item)

    for idx, db_item in enumerate(db_items_in_order):
        db_item.position = idx

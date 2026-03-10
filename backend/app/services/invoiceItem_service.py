from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import DefaultInvoiceItemDB, InvoiceType
from ..schemas import InvoiceItemCreate, InvoiceItemUpdate
from ..schemas.defaultInvoiceItem_schema import DefaultInvoiceItemUpdate, DefaultInvoiceItemCreate


def load_all_default_items(
        db: Session,
) -> list[DefaultInvoiceItemDB]:
    statement = select(DefaultInvoiceItemDB)
    return list(db.scalars(statement).all())


def load_default_items(
        invoice_type: InvoiceType,
        db: Session
) -> list[DefaultInvoiceItemDB]:
    statement = select(DefaultInvoiceItemDB).where(DefaultInvoiceItemDB.type == invoice_type)
    return list(db.scalars(statement).all())


def load_default_item(
        item_id: int,
        db: Session
) -> DefaultInvoiceItemDB:
    statement = select(DefaultInvoiceItemDB).where(DefaultInvoiceItemDB.default_item_id == item_id)
    db_item = db.scalar(statement)

    if not db_item:
        raise HTTPException(status_code=404, detail="Standardleistung konnte nicht gefunden werden.")

    return db_item


def perform_update_default_item(
        item_id: int,
        update_data: DefaultInvoiceItemUpdate,
        db: Session
) -> DefaultInvoiceItemDB:
    db_item = load_default_item(item_id, db)
    data = update_data.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)

    return db_item


def validate_invoice_item(
        item: InvoiceItemCreate | InvoiceItemUpdate | DefaultInvoiceItemCreate,
        inv_type: InvoiceType,
        quantity: int,
        default_item: bool = False
):
    """Validate and enforce item fields."""
    if not default_item and item.amount < 0:
        raise HTTPException(status_code=400, detail="Betrag darf nicht negativ sein.")

    if not item.description:
        raise HTTPException(status_code=400, detail="Beschreibung darf nicht leer sein.")

    if inv_type in [InvoiceType.KG, InvoiceType.GT]:
        item.quantity = quantity
        item.number = None
    elif inv_type == InvoiceType.HP:
        if not item.number:
            raise HTTPException(status_code=400, detail="Ziffer darf nicht leer sein.")

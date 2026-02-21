from typing import Optional

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from ..models import InvoiceType, DefaultInvoiceItemDB
from ..schemas import DefaultInvoiceItem
from ..schemas.defaultInvoiceItem_schema import DefaultInvoiceItemUpdate, DefaultInvoiceItemCreate
from ..services.invoiceItem_service import load_all_default_items, load_default_items, perform_update_default_item, \
    validate_invoice_item
from ..utilities.database import get_db, add_db

router = APIRouter(prefix="/invoice_items", tags=["invoices"])


@router.get("/defaults", response_model=list[DefaultInvoiceItem])
def get_default_invoice_items(
        invoice_type: Optional[InvoiceType] = Query(None),
        db: Session = Depends(get_db)
):
    """Get an or all existing default invoice items."""
    return load_default_items(invoice_type, db) if invoice_type else load_all_default_items(db)


# TODO: This should be called activate or something. editing is strictly forbidden here. Also the logic has to be changed
@router.patch("/defaults/{item_id}", response_model=DefaultInvoiceItem)
def update_default_invoice_item(
        item_id: int,
        item_update: DefaultInvoiceItemUpdate,
        db: Session = Depends(get_db)
):
    """Updates an existing default invoice item."""
    return perform_update_default_item(item_id, item_update, db)


@router.post("/defaults", response_model=DefaultInvoiceItem)
def create_default_invoice_item(
        item_create: DefaultInvoiceItemCreate,
        db: Session = Depends(get_db)
):
    """Creates a new default invoice item."""
    validate_invoice_item(item_create, item_create.type, item_create.quantity, True)
    db_item = DefaultInvoiceItemDB(**item_create.model_dump())
    return add_db(db_item, db)

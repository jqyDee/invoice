from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..models import DefaultInvoiceItemDB, InvoiceType
from ..schemas import DefaultInvoiceItem
from ..schemas.defaultInvoiceItem_schema import DefaultInvoiceItemCreate
from ..services.invoiceItem_service import (
    load_all_default_items,
    load_default_items,
    perform_set_active_state_default_item,
    validate_invoice_item,
)
from ..utilities.database import add_db, get_db
from ..utilities.security import get_current_user

router = APIRouter(prefix="/invoice_items", tags=["invoices"], dependencies=[Depends(get_current_user)])


@router.get("/defaults", response_model=list[DefaultInvoiceItem])
def get_default_invoice_items(invoice_type: InvoiceType | None = Query(None), db: Session = Depends(get_db)):
    """Get an or all existing default invoice items."""
    return load_default_items(invoice_type, db) if invoice_type else load_all_default_items(db)


@router.patch("/defaults/{item_id}", response_model=DefaultInvoiceItem)
def set_active_state_default_invoice_item(item_id: int, item_active: bool, db: Session = Depends(get_db)):
    """Updates an existing default invoice item."""
    return perform_set_active_state_default_item(item_id, item_active, db)


@router.post("/defaults", response_model=DefaultInvoiceItem)
def create_default_invoice_item(item_create: DefaultInvoiceItemCreate, db: Session = Depends(get_db)):
    """Creates a new default invoice item."""
    validate_invoice_item(item_create, item_create.type, item_create.quantity, True)
    db_item = DefaultInvoiceItemDB(**item_create.model_dump())
    return add_db(db_item, db)

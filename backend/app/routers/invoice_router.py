from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from ..utilities.database import get_db, add_db
from ..schemas import Invoice, InvoiceCreate, InvoiceMarkPaidRequest, InvoiceUpdate
from ..services.invoice_service import create_invoice_logic, load_invoice, load_invoices, set_paid, set_payment_due, update_invoice_logic

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/", response_model=list[Invoice])
def get_invoices(
        show_drafts: bool = Query(True),
        only_drafts: bool = Query(False),
        search: Optional[str] = Query(None),
        db: Session = Depends(get_db)
):
    return load_invoices(show_drafts, only_drafts, search, db)


@router.post("/", response_model=Invoice)
def create_invoice(
        invoice_new: InvoiceCreate,
        db: Session = Depends(get_db)
):
    db_invoice = create_invoice_logic(invoice_new, db)
    return add_db(db_invoice, db)


@router.get("/{invoice_id}", response_model=Invoice)
def get_invoice(
        invoice_id: int,
        db: Session = Depends(get_db)
):
    return load_invoice(invoice_id, db)


@router.patch("/{invoice_id}", response_model=Invoice)
def update_invoice(
        invoice_id: int,
        invoice: InvoiceUpdate,
        db: Session = Depends(get_db)
):
    db_invoice = update_invoice_logic(invoice_id, invoice, db)
    return db_invoice

@router.post("/{invoice_id}/payment-due", response_model=Invoice, operation_id="set_payment_due")
def mark_payment_due(invoice_id: int, db: Session = Depends(get_db)):
    return set_payment_due(invoice_id, db)


@router.post("/{invoice_id}/paid", response_model=Invoice, operation_id="set_paid")
def mark_paid(invoice_id: int, body: InvoiceMarkPaidRequest, db: Session = Depends(get_db)):
    return set_paid(invoice_id, body.paid_at, db)


@router.delete("/{invoice_id}", response_model=Invoice)
def delete_invoice(
        invoice_id: int,
        db: Session = Depends(get_db)
):
    db_invoice = load_invoice(invoice_id, db)

    if db_invoice.is_locked:
        raise HTTPException(status_code=403, detail="Rechnung ist bereits gesperrt.")

    db.delete(db_invoice)
    db.commit()
    return db_invoice

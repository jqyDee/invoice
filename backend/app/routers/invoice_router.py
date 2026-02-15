from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from ..utilities.database import get_db, add_db
from ..models import InvoiceDB
from ..schemas import Invoice, InvoiceCreate
from ..services.invoice_service import create_invoice_logic

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/", response_model=list[Invoice])
def get_invoices(
        show_drafts: bool = Query(True),
        only_drafts: bool = Query(False),
        search: Optional[str] = Query(None),
        db: Session = Depends(get_db)
):
    query = db.query(InvoiceDB)

    if only_drafts:
        query = query.filter(InvoiceDB.is_draft == True)

    elif not show_drafts:
        query = query.filter(InvoiceDB.is_draft == False)

    if search:
        query = query.filter(InvoiceDB.invoice_number.ilike(f"%{search}%"))

    return query.all()


@router.get("/{invoice_id}", response_model=Invoice)
def get_invoice(
        invoice_id: str,
        db: Session = Depends(get_db)
):
    return db.query(InvoiceDB).get(invoice_id)


@router.post("/", response_model=Invoice)
def create_invoice(
        invoice_new: InvoiceCreate,
        db: Session = Depends(get_db)
):
    db_invoice = create_invoice_logic(invoice_new, db)
    return add_db(db_invoice, db)

@router.delete("/{invoice_id}", response_model=Invoice)
def delete_invoice(
        invoice_id: str,
        db: Session = Depends(get_db)
):
    db_invoice = db.query(InvoiceDB).options(joinedload(InvoiceDB.patient)).filter(
        InvoiceDB.invoice_id == invoice_id).first()

    if not db_invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    db.delete(db_invoice)
    db.commit()
    return db_invoice
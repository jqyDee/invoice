from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session

from ..utilities.database import get_db
from ..models import InvoiceDB, SettingsDB
from ..utilities.config import CACHE_DIR
from ..services.pdf_service import regenerate_invoice_pdf

router = APIRouter(prefix="/pdf", tags=["pdf"])

# pdf's will be saved by invoice_number.

@router.get("/{invoice_id}")
def get_pdf_invoice(
        invoice_id: int,
        db: Session = Depends(get_db)
):
    settings: SettingsDB | None = db.query(SettingsDB).get(1)

    if not settings:
        raise HTTPException(status_code=404, detail="Bankdetails festlegen")

    invoice: InvoiceDB | None = db.query(InvoiceDB).options(
        joinedload(InvoiceDB.patient),
        joinedload(InvoiceDB.items),
        joinedload(InvoiceDB.dates)
    ).filter(InvoiceDB.invoice_id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    if (
            invoice.pdf_generated_at is None
            or invoice.pdf_generated_at < invoice.updated_at
    ):
        regenerate_invoice_pdf(invoice, settings, db)

    return FileResponse(
        path= CACHE_DIR / f"{invoice.invoice_number}.pdf",
        filename=f"{invoice.invoice_number}.pdf",
        content_disposition_type="inline",
        media_type='application/pdf'
    )
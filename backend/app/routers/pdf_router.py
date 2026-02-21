from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm.session import Session

from ..services.invoice_service import load_invoice
from ..services.settings_service import load_settings
from ..utilities import CACHE_DIR
from ..utilities.database import get_db
from ..services.pdf_service import check_and_regenerate_invoice_pdf

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.get("/{invoice_id}")
def get_pdf_invoice(
        invoice_id: int,
        db: Session = Depends(get_db)
):
    settings = load_settings(db)
    if not settings:
        raise HTTPException(status_code=404, detail="Bankdetails festlegen")

    invoice = load_invoice(invoice_id, db)

    pdf_path = CACHE_DIR / f"{invoice.invoice_number}.pdf"
    check_and_regenerate_invoice_pdf(invoice, settings, pdf_path, db)

    return FileResponse(
        path=pdf_path,
        filename=f"{invoice.invoice_number}.pdf",
        content_disposition_type="inline",
        media_type='application/pdf',
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )

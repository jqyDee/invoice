from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm.session import Session

from ..services.invoice_service import load_invoice
from ..services.patient_service import load_patient
from ..services.pdf_service import (
    check_and_regenerate_invoice_pdf,
    check_and_regenerate_privacy_pdf,
    check_and_regenerate_therapy_pdf,
)
from ..services.settings_service import load_settings
from ..utilities.database import get_db
from ..utilities.path_utilitiy import generate_invoice_path, generate_privacy_path, generate_therapy_path
from ..utilities.security import get_current_user

router = APIRouter(prefix="/pdf", tags=["pdf"], dependencies=[Depends(get_current_user)])


@router.get("/invoice/{invoice_id}")
def get_pdf_invoice(invoice_id: int, db: Session = Depends(get_db)):
    settings = load_settings(db)
    if not settings:
        raise HTTPException(status_code=404, detail="Bankdetails müssen zuerst in den Einstellungen festgelegt werden.")

    invoice = load_invoice(invoice_id, db)

    pdf_path = generate_invoice_path(invoice)
    check_and_regenerate_invoice_pdf(invoice, settings, pdf_path, db)

    return FileResponse(
        path=pdf_path,
        filename=f"{invoice.invoice_number}.pdf",
        content_disposition_type="inline",
        media_type="application/pdf",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@router.get("/therapy/{patient_id}")
def get_pdf_therapy(patient_id: int, db: Session = Depends(get_db)):
    settings = load_settings(db)
    if not settings:
        raise HTTPException(status_code=404, detail="Bankdetails müssen zuerst in den Einstellungen festgelegt werden.")

    patient = load_patient(patient_id, db)

    pdf_path = generate_therapy_path(patient)
    check_and_regenerate_therapy_pdf(patient, settings, db)

    return FileResponse(
        path=pdf_path,
        filename=f"{patient.patient_id}-{patient.label}-therapy.pdf",
        content_disposition_type="inline",
        media_type="application/pdf",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@router.get("/privacy/{patient_id}")
def get_pdf_privacy(patient_id: int, db: Session = Depends(get_db)):
    patient = load_patient(patient_id, db)

    pdf_path = generate_privacy_path(patient)
    check_and_regenerate_privacy_pdf(patient, db)

    return FileResponse(
        path=pdf_path,
        filename=f"{patient.patient_id}-{patient.label}-privacy.pdf",
        content_disposition_type="inline",
        media_type="application/pdf",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )

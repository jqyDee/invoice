import logging
import os
from datetime import datetime, timezone
from fastapi import HTTPException
from pathlib import Path

from sqlalchemy.orm.session import Session

from ..models import InvoiceDB, InvoiceType, SettingsDB, PatientDB
from ..pdf import InvoiceKg
from ..pdf.invoice_hp_pdf import InvoiceHp
from ..pdf.therapy_pdf import Therapy
from ..services.therapyClause_service import load_clauses

logger = logging.getLogger('uvicorn.error')


def check_and_regenerate_invoice_pdf(
        invoice: InvoiceDB,
        settings: SettingsDB,
        pdf_path: Path,
        db: Session
):
    if (
            not os.path.exists(pdf_path)
            or invoice.pdf_generated_at is None
            or invoice.pdf_generated_at < invoice.updated_at
    ):
        logger.debug("Regenerating PDF")
        _regenerate_invoice_pdf(invoice, settings, db)


def _regenerate_invoice_pdf(
        invoice: InvoiceDB,
        settings: SettingsDB,
        db: Session
):
    if invoice.type == InvoiceType.KG:
        try:
            InvoiceKg(invoice, settings)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        try:
            InvoiceHp(invoice, settings)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    now = datetime.now(timezone.utc)

    invoice.pdf_generated_at = now
    invoice.updated_at = now
    db.commit()


def check_and_regenerate_therapy_pdf(
        patient: PatientDB,
        settings: SettingsDB,
        db: Session,
):
    clauses = load_clauses(db)
    try:
        Therapy(patient, settings, clauses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
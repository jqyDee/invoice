import logging
import os
from datetime import datetime, timezone
from fastapi import HTTPException
from pathlib import Path

from sqlalchemy.orm.session import Session

from ..models import InvoiceDB, InvoiceType, SettingsDB, PatientDB
from ..pdf.invoice_hp_pdf import InvoiceHp
from ..pdf.invoice_kg_pdf import InvoiceKgGt
from ..pdf.therapy_pdf import Therapy
from ..pdf.privacy_pdf import Privacy
from ..services.therapyClause_service import load_clauses
from ..services.privacyClause_service import load_privacy_clauses

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
    print(invoice.type)

    print(InvoiceType.__members__)

    if not isinstance(invoice.type, InvoiceType):
        raise HTTPException(status_code=404, detail="Invoice type not found")

    if invoice.type in [InvoiceType.KG, InvoiceType.GT]:
        try:
            InvoiceKgGt(invoice, settings)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif invoice.type == InvoiceType.HP:
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


def check_and_regenerate_privacy_pdf(patient: PatientDB, db: Session):
    clauses = load_privacy_clauses(db)
    try:
        Privacy(patient, clauses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

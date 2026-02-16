import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm.session import Session

from ..models import InvoiceDB, InvoiceType
from ..pdf import InvoiceKg
from ..pdf.invoice_hp_pdf import InvoiceHp

logger = logging.getLogger('uvicorn.error')


def check_and_regenerate_invoice_pdf(invoice: InvoiceDB, settings, pdf_path: Path, db: Session):
    if (
            not os.path.exists(pdf_path)
            or invoice.pdf_generated_at is None
            or invoice.pdf_generated_at < invoice.updated_at
    ):
        logger.debug("Regenerating PDF")
        _regenerate_invoice_pdf(invoice, settings, db)


def _regenerate_invoice_pdf(invoice: InvoiceDB, settings, db: Session):
    if invoice.type == InvoiceType.KG:
        InvoiceKg(invoice, settings)
    else:
        InvoiceHp(invoice, settings)

    now = datetime.now(timezone.utc)

    invoice.pdf_generated_at = now
    invoice.updated_at = now
    db.commit()

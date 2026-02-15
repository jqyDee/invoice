from datetime import datetime, timezone

from sqlalchemy.orm.session import Session

from ..models import InvoiceDB, InvoiceType
from ..pdf import InvoiceKg
from ..pdf.invoice_hp_pdf import InvoiceHp


def regenerate_invoice_pdf(invoice: InvoiceDB, settings, db: Session):
    if invoice.type == InvoiceType.KG:
        InvoiceKg(invoice, settings)
    else:
        InvoiceHp(invoice, settings)

    now = datetime.now(timezone.utc)

    invoice.pdf_generated_at = now
    invoice.updated_at = now
    db.commit()

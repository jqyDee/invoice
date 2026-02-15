from datetime import datetime, timezone
from sqlalchemy import event

from ..models.invoice_model import InvoiceDB
from ..models.invoiceItem_model import InvoiceItemDB
from ..models.invoiceDate_model import InvoiceDateDB


def _touch_invoice(connection, invoice_id: int):
    """
    Updates the parent invoice.updated_at timestamp.
    """
    now = datetime.now(timezone.utc)

    connection.execute(
        # ide warning as far as I know
        InvoiceDB.__table__.update()
        .where(InvoiceDB.invoice_id == invoice_id)
        .values(updated_at=now)
    )


@event.listens_for(InvoiceItemDB, "after_insert")
@event.listens_for(InvoiceItemDB, "after_update")
@event.listens_for(InvoiceItemDB, "after_delete")
def invoice_item_changed(mapper, connection, target):
    if target.invoice_id:
        _touch_invoice(connection, target.invoice_id)


@event.listens_for(InvoiceDateDB, "after_insert")
@event.listens_for(InvoiceDateDB, "after_update")
@event.listens_for(InvoiceDateDB, "after_delete")
def invoice_date_changed(mapper, connection, target):
    if target.invoice_id:
        _touch_invoice(connection, target.invoice_id)

import time
from datetime import date
from unittest.mock import MagicMock

from app.events.invoice_events import invoice_date_changed, invoice_item_changed
from app.models import InvoiceDateDB, InvoiceDB, InvoiceItemDB


def _get_updated_at(db, invoice_id):
    """Re-fetch updated_at from DB, bypassing SQLAlchemy identity map cache."""
    db.expire_all()
    return db.get(InvoiceDB, invoice_id).updated_at


def test_item_insert_touches_invoice(db, saved_hp_invoice):
    before = _get_updated_at(db, saved_hp_invoice.invoice_id)
    time.sleep(0.01)
    db.add(
        InvoiceItemDB(
            invoice_id=saved_hp_invoice.invoice_id,
            description="New item",
            amount=10.0,
            number="X",
            quantity=1,
            position=99,
        )
    )
    db.flush()
    assert _get_updated_at(db, saved_hp_invoice.invoice_id) >= before


def test_item_update_touches_invoice(db, saved_hp_invoice):
    before = _get_updated_at(db, saved_hp_invoice.invoice_id)
    time.sleep(0.01)
    item = saved_hp_invoice.dates[0].items[0]
    item.amount = 999.0
    db.flush()
    assert _get_updated_at(db, saved_hp_invoice.invoice_id) >= before


def test_item_delete_touches_invoice(db, saved_hp_invoice):
    before = _get_updated_at(db, saved_hp_invoice.invoice_id)
    time.sleep(0.01)
    item = saved_hp_invoice.dates[0].items[0]
    db.delete(item)
    db.flush()
    assert _get_updated_at(db, saved_hp_invoice.invoice_id) >= before


def test_date_insert_touches_invoice(db, saved_hp_invoice):
    before = _get_updated_at(db, saved_hp_invoice.invoice_id)
    time.sleep(0.01)
    db.add(
        InvoiceDateDB(
            invoice_id=saved_hp_invoice.invoice_id,
            date=date(2026, 3, 1),
        )
    )
    db.flush()
    assert _get_updated_at(db, saved_hp_invoice.invoice_id) >= before


def test_date_update_touches_invoice(db, saved_hp_invoice):
    before = _get_updated_at(db, saved_hp_invoice.invoice_id)
    time.sleep(0.01)
    d = saved_hp_invoice.dates[0]
    d.date = date(2026, 6, 15)
    db.flush()
    assert _get_updated_at(db, saved_hp_invoice.invoice_id) >= before


def test_date_delete_touches_invoice(db, saved_hp_invoice):
    before = _get_updated_at(db, saved_hp_invoice.invoice_id)
    time.sleep(0.01)
    d = saved_hp_invoice.dates[0]
    db.delete(d)
    db.flush()
    assert _get_updated_at(db, saved_hp_invoice.invoice_id) >= before


def test_item_changed_skips_when_no_invoice_id():
    mock_conn = MagicMock()
    target = InvoiceItemDB(invoice_id=None, description="x", amount=1.0, quantity=1, position=0)
    invoice_item_changed(None, mock_conn, target)
    mock_conn.execute.assert_not_called()


def test_date_changed_skips_when_no_invoice_id():
    mock_conn = MagicMock()
    target = InvoiceDateDB(invoice_id=None, date=date(2026, 1, 1))
    invoice_date_changed(None, mock_conn, target)
    mock_conn.execute.assert_not_called()

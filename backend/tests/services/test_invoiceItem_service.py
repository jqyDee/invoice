import pytest
from fastapi import HTTPException

from app.models import DefaultInvoiceItemPosition, InvoiceType
from app.schemas.defaultInvoiceItem_schema import DefaultInvoiceItemCreate
from app.schemas.invoiceItem_schema import InvoiceItemCreate, InvoiceItemUpdate
from app.services.invoiceItem_service import (
    load_all_default_items,
    load_default_item,
    load_default_items,
    perform_set_active_state_default_item,
    validate_invoice_item,
)


def _make_default_item_create(**kwargs):
    defaults = dict(
        description="Standard Leistung",
        amount=25.0,
        type=InvoiceType.HP,
        position=DefaultInvoiceItemPosition.APPEND,
        is_active_global=True,
        quantity=None,
        number=None,
    )
    defaults.update(kwargs)
    return DefaultInvoiceItemCreate(**defaults)


# ---------------------------------------------------------------------------
# load_all_default_items
# ---------------------------------------------------------------------------


def test_load_all_default_items_empty(db):
    assert load_all_default_items(db) == []


def test_load_all_default_items_returns_all(db, default_item_hp, default_item_kg):
    items = load_all_default_items(db)
    assert len(items) == 2


# ---------------------------------------------------------------------------
# load_default_items
# ---------------------------------------------------------------------------


def test_load_default_items_filters_by_type(db, default_item_hp, default_item_kg):
    hp_items = load_default_items(InvoiceType.HP, db)
    assert all(i.type == InvoiceType.HP for i in hp_items)
    assert len(hp_items) == 1

    kg_items = load_default_items(InvoiceType.KG, db)
    assert len(kg_items) == 1
    assert kg_items[0].type == InvoiceType.KG


def test_load_default_items_returns_empty_for_unknown_type(db, default_item_hp):
    items = load_default_items(InvoiceType.GT, db)
    assert items == []


# ---------------------------------------------------------------------------
# load_default_item
# ---------------------------------------------------------------------------


def test_load_default_item_found(db, default_item_hp):
    result = load_default_item(default_item_hp.default_item_id, db)
    assert result.default_item_id == default_item_hp.default_item_id
    assert result.description == "Fahrtkosten HP"


def test_load_default_item_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        load_default_item(99999, db)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# perform_set_active_state_default_item
# ---------------------------------------------------------------------------


def test_perform_update_default_item_updates_description(db, default_item_hp):
    result = perform_set_active_state_default_item(default_item_hp.default_item_id, False, db)
    assert result.is_active_global == False


def test_perform_update_default_item_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        perform_set_active_state_default_item(99999, True, db)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# validate_invoice_item
# ---------------------------------------------------------------------------


def test_validate_negative_amount_raises_400(db):
    item = InvoiceItemCreate(description="Test", amount=-1.0, number="1")
    with pytest.raises(HTTPException) as exc:
        validate_invoice_item(item, InvoiceType.HP, 1)
    assert exc.value.status_code == 400


def test_validate_empty_description_raises_400(db):
    item = InvoiceItemCreate(description="", amount=10.0, number="1")
    with pytest.raises(HTTPException) as exc:
        validate_invoice_item(item, InvoiceType.HP, 1)
    assert exc.value.status_code == 400


def test_validate_kg_sets_quantity_to_date_count():
    item = InvoiceItemCreate(description="KG Leistung", amount=30.0, quantity=1)
    validate_invoice_item(item, InvoiceType.KG, 5)
    assert item.quantity == 5


def test_validate_kg_clears_number():
    item = InvoiceItemCreate(description="KG Leistung", amount=30.0, number="XYZ", quantity=1)
    validate_invoice_item(item, InvoiceType.KG, 3)
    assert item.number is None


def test_validate_gt_sets_quantity_to_date_count():
    item = InvoiceItemCreate(description="GT Leistung", amount=20.0, quantity=1)
    validate_invoice_item(item, InvoiceType.GT, 4)
    assert item.quantity == 4


def test_validate_hp_missing_number_raises_400():
    item = InvoiceItemCreate(description="Behandlung", amount=50.0, number=None)
    with pytest.raises(HTTPException) as exc:
        validate_invoice_item(item, InvoiceType.HP, 1)
    assert exc.value.status_code == 400


def test_validate_hp_with_number_passes():
    item = InvoiceItemCreate(description="Behandlung", amount=50.0, number="GÖÄ 1")
    validate_invoice_item(item, InvoiceType.HP, 1)  # no exception


def test_validate_default_item_allows_negative_amount():
    item = InvoiceItemCreate(description="Rabatt", amount=-5.0, number="1")
    validate_invoice_item(item, InvoiceType.HP, 1, default_item=True)  # no exception


def test_validate_zero_amount_is_allowed():
    item = InvoiceItemCreate(description="Kostenlos", amount=0.0, number="1")
    validate_invoice_item(item, InvoiceType.HP, 1)  # no exception


def test_validate_update_schema_also_works():
    item = InvoiceItemUpdate(description="Update Test", amount=10.0, number="GÖÄ 2")
    validate_invoice_item(item, InvoiceType.HP, 1)  # no exception

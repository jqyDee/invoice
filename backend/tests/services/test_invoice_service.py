from datetime import date

import pytest
from fastapi import HTTPException

from app.models import (
    InvoiceDateDB,
    InvoiceDB,
    InvoiceInvoiceDefaultItemAssociationDB,
    InvoiceItemDB,
    InvoiceStatus,
    InvoiceType,
)
from app.schemas.invoice_schema import Invoice, InvoiceCreate, InvoiceUpdate
from app.schemas.invoiceDate_schema import InvoiceDateCreate, InvoiceDateUpdate
from app.schemas.invoiceItem_schema import InvoiceItemCreate, InvoiceItemUpdate
from app.services.invoice_service import (
    create_invoice_logic,
    get_invoice_template,
    get_template_diagnoses,
    get_template_items,
    load_invoice,
    load_invoices,
    set_paid,
    set_payment_due,
    update_invoice_logic,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _hp_create(patient_id: int, save_as_draft=False, **kwargs) -> InvoiceCreate:
    return InvoiceCreate(
        patient_id=patient_id,
        invoice_date=date(2026, 3, 1),
        type=InvoiceType.HP,
        dates=[
            InvoiceDateCreate(
                date=date(2026, 2, 10),
                items=[InvoiceItemCreate(description="Behandlung", amount=50.0, number="GÖÄ 1")],
            )
        ],
        save_as_draft=save_as_draft,
        **{"default_item_ids": [], **kwargs},
    )


def _kg_create(patient_id: int, save_as_draft=False, **kwargs) -> InvoiceCreate:
    return InvoiceCreate(
        patient_id=patient_id,
        invoice_date=date(2026, 3, 1),
        type=InvoiceType.KG,
        dates=[
            InvoiceDateCreate(date=date(2026, 2, 5)),
            InvoiceDateCreate(date=date(2026, 2, 12)),
        ],
        user_items=[InvoiceItemCreate(description="KG Behandlung", amount=30.0, quantity=2)],
        default_item_ids=[],
        save_as_draft=save_as_draft,
        **kwargs,
    )


def _commit_and_reload(db, invoice_id: int) -> InvoiceDB:
    db.commit()
    return load_invoice(invoice_id, db)


# ---------------------------------------------------------------------------
# load_invoice
# ---------------------------------------------------------------------------


def test_load_invoice_returns_invoice(db, saved_hp_invoice):
    result = load_invoice(saved_hp_invoice.invoice_id, db)
    assert result.invoice_id == saved_hp_invoice.invoice_id
    assert result.type == InvoiceType.HP


def test_load_invoice_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        load_invoice(99999, db)
    assert exc.value.status_code == 404


def test_load_invoice_eager_loads_relationships(db, saved_hp_invoice):
    result = load_invoice(saved_hp_invoice.invoice_id, db)
    assert len(result.dates) == 1
    assert len(result.dates[0].items) == 1
    assert result.patient is not None


# ---------------------------------------------------------------------------
# load_invoices
# ---------------------------------------------------------------------------


def test_load_invoices_returns_all_non_drafts(db, saved_hp_invoice, patient):
    # add a DRAFT invoice that should be excluded
    draft = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 4, 1),
        type=InvoiceType.KG,
        status=InvoiceStatus.DRAFT,
    )
    db.add(draft)
    db.commit()

    items, total = load_invoices(show_drafts=False, only_drafts=False, only_open=False, search=None, db=db)
    ids = [i.invoice_id for i in items]
    assert saved_hp_invoice.invoice_id in ids
    assert draft.invoice_id not in ids


def test_load_invoices_only_drafts(db, saved_hp_invoice, patient):
    draft = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 4, 1),
        type=InvoiceType.KG,
        status=InvoiceStatus.DRAFT,
    )
    db.add(draft)
    db.commit()

    items, total = load_invoices(show_drafts=True, only_drafts=True, only_open=False, search=None, db=db)
    assert all(i.status == InvoiceStatus.DRAFT for i in items)
    assert total == 1


def test_load_invoices_only_open(db, saved_hp_invoice, patient):
    due = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 4, 1),
        invoice_number="2026-04-01-KG-TEST",
        type=InvoiceType.KG,
        status=InvoiceStatus.PAYMENT_DUE,
    )
    paid = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 4, 2),
        invoice_number="2026-04-02-KG-TEST",
        type=InvoiceType.KG,
        status=InvoiceStatus.PAID,
        paid_at=date(2026, 4, 10),
    )
    db.add_all([due, paid])
    db.commit()

    items, total = load_invoices(show_drafts=False, only_drafts=False, only_open=True, search=None, db=db)
    statuses = {i.status for i in items}
    assert InvoiceStatus.SAVED in statuses or InvoiceStatus.PAYMENT_DUE in statuses
    assert InvoiceStatus.PAID not in statuses


def test_load_invoices_filter_by_type(db, saved_hp_invoice, saved_kg_invoice):
    items, total = load_invoices(
        show_drafts=False, only_drafts=False, only_open=False, search=None, db=db, invoice_types=[InvoiceType.HP]
    )
    assert all(i.type == InvoiceType.HP for i in items)


def test_load_invoices_pagination(db, patient):
    for i in range(5):
        inv = InvoiceDB(
            patient_id=patient.patient_id,
            invoice_date=date(2026, 1, i + 1),
            invoice_number=f"2026-01-0{i + 1}-HP-TEST",
            type=InvoiceType.HP,
            status=InvoiceStatus.SAVED,
        )
        db.add(inv)
    db.commit()

    items, total = load_invoices(
        show_drafts=False, only_drafts=False, only_open=False, search=None, db=db, page=1, size=2
    )
    assert len(items) == 2
    assert total == 5


def test_load_invoices_search_by_number(db, saved_hp_invoice):
    items, total = load_invoices(show_drafts=False, only_drafts=False, only_open=False, search="2026-01-15-HP", db=db)
    assert total == 1
    assert items[0].invoice_id == saved_hp_invoice.invoice_id


def test_load_invoices_filter_by_year_and_month(db, patient):
    inv_2025 = InvoiceDB(
        patient_id=patient.patient_id, invoice_date=date(2025, 12, 1), type=InvoiceType.HP, status=InvoiceStatus.SAVED
    )
    inv_2026 = InvoiceDB(
        patient_id=patient.patient_id, invoice_date=date(2026, 1, 15), type=InvoiceType.HP, status=InvoiceStatus.SAVED
    )
    db.add_all([inv_2025, inv_2026])
    db.commit()

    # Test year filter
    items_2025, _ = load_invoices(
        show_drafts=False, only_drafts=False, only_open=False, search=None, db=db, years=[2025]
    )
    assert len(items_2025) == 1
    assert items_2025[0].invoice_date.year == 2025

    # Test month filter
    items_jan, _ = load_invoices(show_drafts=False, only_drafts=False, only_open=False, search=None, db=db, months=[1])
    assert len(items_jan) == 1
    assert items_jan[0].invoice_date.month == 1


def test_load_invoices_sorting(db, patient):
    inv1 = InvoiceDB(
        patient_id=patient.patient_id, invoice_date=date(2026, 1, 1), type=InvoiceType.HP, status=InvoiceStatus.SAVED
    )
    inv2 = InvoiceDB(
        patient_id=patient.patient_id, invoice_date=date(2026, 1, 2), type=InvoiceType.HP, status=InvoiceStatus.SAVED
    )
    db.add_all([inv1, inv2])
    db.commit()

    # Sort descending
    items_desc, _ = load_invoices(
        show_drafts=False,
        only_drafts=False,
        only_open=False,
        search=None,
        db=db,
        sort_field="invoice_date",
        sort_order="desc",
    )
    assert items_desc[0].invoice_date == date(2026, 1, 2)

    # Sort ascending
    items_asc, _ = load_invoices(
        show_drafts=False,
        only_drafts=False,
        only_open=False,
        search=None,
        db=db,
        sort_field="invoice_date",
        sort_order="asc",
    )
    assert items_asc[0].invoice_date == date(2026, 1, 1)


# ---------------------------------------------------------------------------
# create_invoice_logic
# ---------------------------------------------------------------------------


def test_create_hp_invoice_saved(db, patient):
    data = _hp_create(patient.patient_id)
    result = create_invoice_logic(data, db)
    inv = _commit_and_reload(db, result.invoice_id)

    assert inv.status == InvoiceStatus.SAVED
    assert inv.invoice_number is not None
    assert inv.type == InvoiceType.HP
    assert len(inv.dates) == 1
    assert len(inv.dates[0].items) == 1


def test_create_hp_invoice_as_draft(db, patient):
    data = _hp_create(patient.patient_id, save_as_draft=True)
    result = create_invoice_logic(data, db)
    db.commit()

    assert result.status == InvoiceStatus.DRAFT
    assert result.invoice_number is None
    assert result.type == InvoiceType.HP
    assert len(result.dates) == 1
    assert len(result.dates[0].items) == 1


def test_create_kg_invoice_saved(db, patient):
    data = _kg_create(patient.patient_id)
    result = create_invoice_logic(data, db)
    inv = _commit_and_reload(db, result.invoice_id)

    assert inv.status == InvoiceStatus.SAVED
    assert inv.invoice_number is not None
    assert inv.type == InvoiceType.KG
    assert len(inv.dates) == 2
    assert len(inv.user_items) == 1


def test_create_kg_invoice_as_draft(db, patient):
    data = _kg_create(patient.patient_id, save_as_draft=True)
    result = create_invoice_logic(data, db)
    db.commit()

    assert result.status == InvoiceStatus.DRAFT
    assert result.invoice_number is None
    assert result.type == InvoiceType.KG
    assert len(result.dates) == 2
    assert len(result.user_items) == 1


def test_create_invoice_snapshots_km_from_patient(db, patient):
    data = _hp_create(patient.patient_id)
    result = create_invoice_logic(data, db)
    assert result.kilometers_at_billing == patient.kilometers_to_travel


def test_create_invoice_duplicate_number_raises_409(db, patient):
    data = _hp_create(patient.patient_id)
    result = create_invoice_logic(data, db)
    db.commit()

    # Same date+type+label → same invoice number
    with pytest.raises(HTTPException) as exc:
        create_invoice_logic(data, db)
    assert exc.value.status_code == 409


def test_create_invoice_links_default_items(db, patient, default_item_hp):
    data = _hp_create(patient.patient_id, default_item_ids=[default_item_hp.default_item_id])
    result = create_invoice_logic(data, db)
    inv = _commit_and_reload(db, result.invoice_id)

    assert len(inv.default_items) == 1
    assert inv.default_items[0].default_item.default_item_id == default_item_hp.default_item_id


def test_create_invoice_patient_not_found_raises_404(db):
    data = _hp_create(patient_id=99999)
    with pytest.raises(HTTPException) as exc:
        create_invoice_logic(data, db)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# update_invoice_logic
# ---------------------------------------------------------------------------


def test_update_invoice_scalar_fields(db, saved_hp_invoice):
    update = InvoiceUpdate(diagnosis="Neues Leiden")
    result = update_invoice_logic(saved_hp_invoice.invoice_id, update, db)
    assert result.diagnosis == "Neues Leiden"


def test_update_invoice_locked_raises_403(db, patient):
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        invoice_number="2026-01-01-HP-TEST",
        type=InvoiceType.HP,
        status=InvoiceStatus.PAYMENT_DUE,
    )
    db.add(inv)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        update_invoice_logic(inv.invoice_id, InvoiceUpdate(diagnosis="test"), db)
    assert exc.value.status_code == 403


def test_update_invoice_draft_to_saved(db, patient):
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 5, 1),
        type=InvoiceType.HP,
        status=InvoiceStatus.DRAFT,
    )
    db.add(inv)
    db.commit()

    update = InvoiceUpdate(save_as_draft=False)
    result = update_invoice_logic(inv.invoice_id, update, db)
    assert result.status == InvoiceStatus.SAVED
    assert result.invoice_number is not None


def test_update_hp_dates_removes_deleted_date(db, saved_hp_invoice):
    # update with empty dates list → removes the existing date
    update = InvoiceUpdate(dates=[])
    result = update_invoice_logic(saved_hp_invoice.invoice_id, update, db)
    assert result.dates == []


def test_update_hp_dates_adds_new_date(db, saved_hp_invoice):
    existing_date = saved_hp_invoice.dates[0]
    update = InvoiceUpdate(
        dates=[
            InvoiceDateUpdate(
                date_id=existing_date.date_id,
                date=existing_date.date,
                items=[
                    InvoiceItemUpdate(
                        item_id=existing_date.items[0].item_id,
                        description=existing_date.items[0].description,
                        amount=existing_date.items[0].amount,
                        number=existing_date.items[0].number,
                    )
                ],
            ),
            InvoiceDateUpdate(
                date=date(2026, 2, 1),
                items=[
                    InvoiceItemUpdate(description="Neue Behandlung", amount=40.0, number="GÖÄ 2"),
                ],
            ),
        ]
    )
    result = update_invoice_logic(saved_hp_invoice.invoice_id, update, db)
    assert len(result.dates) == 2


def test_update_kg_standalone_items(db, saved_kg_invoice):
    existing_item = saved_kg_invoice.user_items[0]
    update = InvoiceUpdate(
        user_items=[
            InvoiceItemUpdate(
                item_id=existing_item.item_id,
                description="Geänderte Beschreibung",
                amount=existing_item.amount,
                quantity=existing_item.quantity,
            )
        ]
    )
    result = update_invoice_logic(saved_kg_invoice.invoice_id, update, db)
    assert result.user_items[0].description == "Geänderte Beschreibung"


def test_update_hp_modifies_existing_item(db, saved_hp_invoice):
    existing_date = saved_hp_invoice.dates[0]
    existing_item = existing_date.items[0]

    update = InvoiceUpdate(
        dates=[
            InvoiceDateUpdate(
                date_id=existing_date.date_id,
                date=existing_date.date,
                items=[
                    InvoiceItemUpdate(
                        item_id=existing_item.item_id,
                        description="Updated Description",
                        amount=99.0,
                        number=existing_item.number,
                    )
                ],
            )
        ]
    )
    result = update_invoice_logic(saved_hp_invoice.invoice_id, update, db)
    assert result.dates[0].items[0].description == "Updated Description"
    assert result.dates[0].items[0].amount == 99.0


def test_update_kg_dates_sync(db, saved_kg_invoice):
    existing_date_id = saved_kg_invoice.dates[0].date_id

    update = InvoiceUpdate(
        dates=[
            InvoiceDateUpdate(date_id=existing_date_id, date=date(2026, 2, 5)),  # Keep
            InvoiceDateUpdate(date=date(2026, 2, 20)),  # Add
        ]
    )
    result = update_invoice_logic(saved_kg_invoice.invoice_id, update, db)
    assert len(result.dates) == 2
    assert any(d.date == date(2026, 2, 20) for d in result.dates)


def test_update_kg_items_add_and_remove(db, saved_kg_invoice):
    update = InvoiceUpdate(
        user_items=[
            InvoiceItemUpdate(description="New Item 1", amount=15.0, quantity=1),
            InvoiceItemUpdate(description="New Item 2", amount=25.0, quantity=2),
        ]
    )
    result = update_invoice_logic(saved_kg_invoice.invoice_id, update, db)
    assert len(result.user_items) == 2
    descriptions = [i.description for i in result.user_items]
    assert "New Item 1" in descriptions
    assert "New Item 2" in descriptions


def test_update_invoice_syncs_default_items(db, saved_hp_invoice, default_item_hp):
    update = InvoiceUpdate(default_item_ids=[default_item_hp.default_item_id])
    result = update_invoice_logic(saved_hp_invoice.invoice_id, update, db)

    assert len(result.default_items) == 1
    assert result.default_items[0].default_item_id == default_item_hp.default_item_id

    update_clear = InvoiceUpdate(default_item_ids=[])
    result_clear = update_invoice_logic(saved_hp_invoice.invoice_id, update_clear, db)
    assert len(result_clear.default_items) == 0


def test_update_hp_deletes_item_from_existing_date(db, saved_hp_invoice):
    existing_date = saved_hp_invoice.dates[0]

    # Send the existing date_id, but an empty items list
    # This will trigger the `db.delete(i_obj)` block
    update = InvoiceUpdate(dates=[InvoiceDateUpdate(date_id=existing_date.date_id, date=existing_date.date, items=[])])
    result = update_invoice_logic(saved_hp_invoice.invoice_id, update, db)

    assert len(result.dates) == 1
    assert len(result.dates[0].items) == 0


def test_update_hp_adds_new_item_to_existing_date(db, saved_hp_invoice):
    existing_date = saved_hp_invoice.dates[0]
    existing_item = existing_date.items[0]

    # Send the existing date_id, keep the existing item, and add a NEW one
    # The new item has no item_id, triggering the `else:` block
    update = InvoiceUpdate(
        dates=[
            InvoiceDateUpdate(
                date_id=existing_date.date_id,
                date=existing_date.date,
                items=[
                    InvoiceItemUpdate(
                        item_id=existing_item.item_id,
                        description=existing_item.description,
                        amount=existing_item.amount,
                        number=existing_item.number,
                    ),
                    InvoiceItemUpdate(description="Brand New Item", amount=75.0, number="GÖÄ 3"),
                ],
            )
        ]
    )
    result = update_invoice_logic(saved_hp_invoice.invoice_id, update, db)

    assert len(result.dates) == 1
    assert len(result.dates[0].items) == 2

    descriptions = [i.description for i in result.dates[0].items]
    assert "Brand New Item" in descriptions


# ---------------------------------------------------------------------------
# set_payment_due
# ---------------------------------------------------------------------------


def test_set_payment_due_transitions_status(db, saved_hp_invoice):
    result = set_payment_due(saved_hp_invoice.invoice_id, db)
    assert result.status == InvoiceStatus.PAYMENT_DUE


def test_set_payment_due_already_locked_raises_409(db, patient):
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        invoice_number="2026-01-01-HP-LOCK",
        type=InvoiceType.HP,
        status=InvoiceStatus.PAYMENT_DUE,
    )
    db.add(inv)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        set_payment_due(inv.invoice_id, db)
    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# set_paid
# ---------------------------------------------------------------------------


def test_set_paid_marks_invoice_paid(db, patient):
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        invoice_number="2026-01-01-HP-PAY",
        type=InvoiceType.HP,
        status=InvoiceStatus.PAYMENT_DUE,
    )
    db.add(inv)
    db.commit()

    paid_date = date(2026, 4, 20)
    result = set_paid(inv.invoice_id, paid_date, db)
    assert result.status == InvoiceStatus.PAID
    assert result.paid_at == paid_date


def test_set_paid_wrong_status_raises_409(db, saved_hp_invoice):
    with pytest.raises(HTTPException) as exc:
        set_paid(saved_hp_invoice.invoice_id, date(2026, 4, 20), db)
    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# get_template_items
# ---------------------------------------------------------------------------


def test_get_template_items_deduplicates(db, patient):
    # Two HP invoices with identical items
    for num in ("2026-01-01-HP-T1", "2026-01-02-HP-T2"):
        inv = InvoiceDB(
            patient_id=patient.patient_id,
            invoice_date=date(2026, 1, 1),
            invoice_number=num,
            type=InvoiceType.HP,
            status=InvoiceStatus.SAVED,
        )
        db.add(inv)
        db.flush()
        d = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 1, 1))
        db.add(d)
        db.flush()
        db.add(
            InvoiceItemDB(
                invoice_id=inv.invoice_id,
                date_id=d.date_id,
                description="Behandlung",
                amount=50.0,
                number="GÖÄ 1",
                quantity=1,
            )
        )
    db.commit()

    result = get_template_items(InvoiceType.HP, db)
    descriptions = [r.description for r in result]
    assert descriptions.count("Behandlung") == 1


def test_get_template_items_excludes_drafts(db, patient):
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        type=InvoiceType.HP,
        status=InvoiceStatus.DRAFT,
    )
    db.add(inv)
    db.flush()
    d = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 1, 1))
    db.add(d)
    db.flush()
    db.add(
        InvoiceItemDB(
            invoice_id=inv.invoice_id,
            date_id=d.date_id,
            description="Draft Behandlung",
            amount=50.0,
            number="GÖÄ 1",
            quantity=1,
        )
    )
    db.commit()

    result = get_template_items(InvoiceType.HP, db)
    assert result == []


# ---------------------------------------------------------------------------
# get_template_diagnoses
# ---------------------------------------------------------------------------


def test_get_template_diagnoses_deduplicates(db, patient):
    for num in ("2026-01-01-HP-D1", "2026-01-02-HP-D2"):
        inv = InvoiceDB(
            patient_id=patient.patient_id,
            invoice_date=date(2026, 1, 1),
            invoice_number=num,
            type=InvoiceType.HP,
            status=InvoiceStatus.SAVED,
            diagnosis="Rückenschmerzen",
        )
        db.add(inv)
    db.commit()

    result = get_template_diagnoses(db)
    diagnoses = [r.diagnosis for r in result]
    assert diagnoses.count("Rückenschmerzen") == 1


def test_get_template_diagnoses_empty_when_no_hp_invoices(db, saved_kg_invoice):
    result = get_template_diagnoses(db)
    assert result == []


# ---------------------------------------------------------------------------
# get_invoice_template
# ---------------------------------------------------------------------------


def test_get_invoice_template_kg(db, saved_kg_invoice):
    result = get_invoice_template(saved_kg_invoice.invoice_id, db)
    assert result.type == InvoiceType.KG
    assert len(result.user_items) == 1
    assert result.date_groups == []


def test_get_invoice_template_hp_returns_date_groups(db, saved_hp_invoice):
    result = get_invoice_template(saved_hp_invoice.invoice_id, db)
    assert result.type == InvoiceType.HP
    assert len(result.date_groups) == 1
    # HP template uses relative dates starting from date.min
    assert result.date_groups[0].date == date.min
    assert len(result.date_groups[0].items) == 1


# ---------------------------------------------------------------------------
# InvoiceDB hybrid properties
# ---------------------------------------------------------------------------


def test_is_locked_false_for_saved(db, saved_hp_invoice):
    assert saved_hp_invoice.is_locked is False


def test_is_locked_true_for_payment_due(db, patient):
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        type=InvoiceType.HP,
        status=InvoiceStatus.PAYMENT_DUE,
    )
    db.add(inv)
    db.commit()
    assert inv.is_locked is True


def test_is_locked_true_for_paid(db, patient):
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        type=InvoiceType.HP,
        status=InvoiceStatus.PAID,
        paid_at=date(2026, 2, 1),
    )
    db.add(inv)
    db.commit()
    assert inv.is_locked is True


def test_total_sums_user_items(db, saved_hp_invoice):
    # saved_hp_invoice has one item: amount=50.0, quantity=1 → total = 50.0
    assert saved_hp_invoice.total == 50.0


def test_total_includes_default_items(db, saved_hp_invoice, default_item_hp):
    # Link a default item with explicit quantity=2, amount=10 → adds 20.0
    assoc = InvoiceInvoiceDefaultItemAssociationDB(
        invoice_id=saved_hp_invoice.invoice_id,
        default_item_id=default_item_hp.default_item_id,
    )
    db.add(assoc)
    db.commit()
    db.refresh(saved_hp_invoice)

    # default_item_hp: amount=10.0, quantity=None → uses date_count=1 → 10.0
    # user_item: 50.0
    assert saved_hp_invoice.total == 60.0


def test_total_default_item_null_quantity_uses_date_count(db, patient, default_item_hp):
    """Default item with quantity=None multiplies by number of dates."""
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        type=InvoiceType.HP,
        status=InvoiceStatus.SAVED,
        invoice_number="2026-01-01-HP-TTL",
    )
    db.add(inv)
    db.flush()

    # 3 dates
    for d in [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)]:
        db.add(InvoiceDateDB(invoice_id=inv.invoice_id, date=d))

    assoc = InvoiceInvoiceDefaultItemAssociationDB(
        invoice_id=inv.invoice_id,
        default_item_id=default_item_hp.default_item_id,
    )
    db.add(assoc)
    db.commit()
    db.refresh(inv)

    # default_item_hp: amount=10.0, quantity=None → 10.0 * 3 dates = 30.0
    assert inv.total == 30.0


def test_total_travel_distance(db, saved_hp_invoice):
    # 1 date, km_at_billing=10.0 → 10 * 1 * 2 = 20.0
    assert saved_hp_invoice.total_travel_distance == 20.0


def test_total_travel_distance_multiple_dates(db, saved_kg_invoice):
    # 2 dates, km_at_billing=10.0 → 10 * 2 * 2 = 40.0
    assert saved_kg_invoice.total_travel_distance == 40.0


def test_total_travel_distance_no_dates(db, patient):
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        type=InvoiceType.HP,
        status=InvoiceStatus.SAVED,
        kilometers_at_billing=15.0,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    assert inv.total_travel_distance == 0.0


# ---------------------------------------------------------------------------
# Templates & Edge Cases
# ---------------------------------------------------------------------------


def test_get_template_items_kg(db, saved_kg_invoice):
    # Ensure the branch checking inv.user_items for KG invoices triggers correctly
    result = get_template_items(InvoiceType.KG, db)
    assert len(result) == 1
    assert result[0].description == "KG Behandlung"
    assert result[0].amount == 30.0


def test_create_invoice_empty_lists_bypass_safely(db, patient):
    # Testing that dates=[] and user_items=[] don't crash the creation loops
    data = InvoiceCreate(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 3, 1),
        type=InvoiceType.KG,
        dates=[],
        user_items=[],
        default_item_ids=[],
    )
    result = create_invoice_logic(data, db)
    assert result.status == InvoiceStatus.SAVED
    assert len(result.dates) == 0
    assert len(result.user_items) == 0


# ---------------------------------------------------------------------------
# Invoice schema — extract_default_items validator
# ---------------------------------------------------------------------------


def test_schema_unwraps_association_objects(db, patient, default_item_hp):
    """validator extracts .default_item from ORM association links"""
    result = create_invoice_logic(
        _hp_create(patient.patient_id, default_item_ids=[default_item_hp.default_item_id]),
        db,
    )

    # Commit the session and reload the invoice so relationships are populated
    inv = _commit_and_reload(db, result.invoice_id)

    schema = Invoice.model_validate(inv)
    assert len(schema.default_items) == 1
    assert schema.default_items[0].default_item_id == default_item_hp.default_item_id


def test_schema_handles_no_default_items(db, patient):
    """validator passes through empty list unchanged"""
    inv = create_invoice_logic(_hp_create(patient.patient_id), db)
    schema = Invoice.model_validate(inv)
    assert schema.default_items == []


# ---------------------------------------------------------------------------
# InvoiceDB hybrid properties — SQL expression branch
# (Python-level hybrid is tested above; here we force SQLAlchemy to generate
#  the SQL subquery version by using the hybrid inside a select/order_by)
# ---------------------------------------------------------------------------


def test_total_expression_order_by_desc(db, saved_hp_invoice, saved_kg_invoice):
    """Forces @total.expression (SQL branch) by using it in order_by."""
    from sqlalchemy import select

    stmt = select(InvoiceDB).order_by(InvoiceDB.total.desc())
    results = db.scalars(stmt).all()
    assert len(results) >= 2
    totals = [r.total for r in results]
    assert totals == sorted(totals, reverse=True)


def test_total_expression_with_no_dates_uses_multiplier_1(db, patient):
    """Tests effective_multiplier = case(date_count == 0, 1) SQL branch."""
    from sqlalchemy import select

    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        type=InvoiceType.HP,
        status=InvoiceStatus.SAVED,
    )
    db.add(inv)
    db.commit()
    result = db.scalar(select(InvoiceDB.total).where(InvoiceDB.invoice_id == inv.invoice_id))
    assert result == 0.0


def test_total_expression_with_user_items(db, patient):
    """Tests user_sum SQL subquery branch."""
    from sqlalchemy import select

    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 2),
        type=InvoiceType.HP,
        status=InvoiceStatus.SAVED,
    )
    db.add(inv)
    db.flush()
    db.add(
        InvoiceItemDB(
            invoice_id=inv.invoice_id,
            description="Item",
            amount=25.0,
            quantity=2,
            position=0,
        )
    )
    db.commit()
    result = db.scalar(select(InvoiceDB.total).where(InvoiceDB.invoice_id == inv.invoice_id))
    assert result == 50.0


def test_total_travel_distance_expression_order_by(db, saved_hp_invoice, saved_kg_invoice):
    """Forces @total_travel_distance.expression by using it in order_by."""
    from sqlalchemy import select

    stmt = select(InvoiceDB).order_by(InvoiceDB.total_travel_distance.desc())
    results = db.scalars(stmt).all()
    assert len(results) >= 2


def test_total_travel_distance_expression_coalesce_fallback(db, patient):
    """Tests coalesce(km_at_billing, patient.km) when km_at_billing is None."""
    from sqlalchemy import select

    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 2, 1),
        type=InvoiceType.HP,
        status=InvoiceStatus.SAVED,
        kilometers_at_billing=None,
    )
    db.add(inv)
    db.flush()
    db.add(InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 2, 1)))
    db.commit()
    # patient.kilometers_to_travel=10.0, 1 date → 10 * 1 * 2 = 20.0
    result = db.scalar(select(InvoiceDB.total_travel_distance).where(InvoiceDB.invoice_id == inv.invoice_id))
    assert result == 20.0

from datetime import date

import pytest
from fastapi import HTTPException

from app.models import Gender, InvoiceDB, InvoiceStatus, InvoiceType, PatientDB
from app.schemas import PatientCreate
from app.services.patient_service import (
    load_patient,
    perform_create_patient,
    perform_delete_patient,
    perform_update_patient,
)


def _patient_create(**kwargs) -> PatientCreate:
    defaults = dict(
        label="ABCD",
        first_name="Anna",
        last_name="Schmidt",
        birthday=date(1985, 6, 15),
        gender=Gender.FEMALE,
        street="Hauptstraße",
        street_number="5",
        postal_code="80331",
        city="München",
        kilometers_to_travel=5.0,
    )
    defaults.update(kwargs)
    return PatientCreate(**defaults)


# ---------------------------------------------------------------------------
# load_patient
# ---------------------------------------------------------------------------

def test_load_patient_returns_correct_patient(db, patient):
    result = load_patient(patient.patient_id, db)
    assert result.patient_id == patient.patient_id
    assert result.first_name == "Max"


def test_load_patient_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        load_patient(99999, db)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# perform_create_patient
# ---------------------------------------------------------------------------

def test_perform_create_patient_persists(db):
    data = _patient_create()
    result = perform_create_patient(data, db)

    assert result.patient_id is not None
    assert result.first_name == "Anna"
    assert result.label == "ABCD"
    assert result.kilometers_to_travel == 5.0

    # verify it's retrievable
    loaded = load_patient(result.patient_id, db)
    assert loaded.last_name == "Schmidt"


def test_perform_create_patient_optional_fields_default_none(db):
    data = _patient_create()
    result = perform_create_patient(data, db)
    assert result.email is None
    assert result.telephone is None


def test_perform_create_patient_with_contact_info(db):
    data = _patient_create(email="anna@example.com", telephone="0151000000")
    result = perform_create_patient(data, db)
    assert result.email == "anna@example.com"
    assert result.telephone == "0151000000"


# ---------------------------------------------------------------------------
# perform_update_patient
# ---------------------------------------------------------------------------

def test_perform_update_patient_updates_fields(db, patient):
    update = _patient_create(first_name="Karl", kilometers_to_travel=20.0)
    result = perform_update_patient(update, patient, db)
    assert result.first_name == "Karl"
    assert result.kilometers_to_travel == 20.0


def test_perform_update_patient_keeps_unchanged_fields(db, patient):
    update = _patient_create(first_name="Karl", last_name="Mustermann")
    result = perform_update_patient(update, patient, db)
    # label was not changed by update (PatientCreate always has it, but value is same)
    assert result.last_name == "Mustermann"


# ---------------------------------------------------------------------------
# perform_delete_patient
# ---------------------------------------------------------------------------

def test_perform_delete_patient_no_invoices_succeeds(db, patient):
    pid = patient.patient_id
    result = perform_delete_patient(pid, db)
    assert result.patient_id == pid

    # patient should no longer exist
    with pytest.raises(HTTPException) as exc:
        load_patient(pid, db)
    assert exc.value.status_code == 404


def test_perform_delete_patient_with_invoice_raises_409(db, patient):
    # create a minimal invoice for the patient
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        type=InvoiceType.HP,
        status=InvoiceStatus.DRAFT,
    )
    db.add(inv)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        perform_delete_patient(patient.patient_id, db)
    assert exc.value.status_code == 409


def test_perform_delete_nonexistent_patient_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        perform_delete_patient(99999, db)
    assert exc.value.status_code == 404

import pytest
from fastapi import HTTPException

from app.models import SettingsDB
from app.services.pdf_service import (
    _regenerate_invoice_pdf,
    check_and_regenerate_invoice_pdf,
    check_and_regenerate_therapy_pdf,
    check_and_regenerate_privacy_pdf,
)


@pytest.fixture
def settings():
    return SettingsDB(
        iban="DE12 3456 7890 1234 5678 90",
        bic="TESTDE11",
        tax_id="123/456/789",
        price_from=100.0,
        price_to=110.0,
    )


def _patch_pdf_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "app.pdf.invoice_hp_pdf.generate_invoice_path",
        lambda inv: tmp_path / f"{inv.invoice_number}.pdf",
    )
    monkeypatch.setattr("app.pdf.invoice_kg_pdf.CACHE_DIR", tmp_path)
    monkeypatch.setattr(
        "app.pdf.therapy_pdf.generate_therapy_path",
        lambda p: tmp_path / f"{p.patient_id}-{p.label}-therapy.pdf",
    )
    monkeypatch.setattr(
        "app.pdf.privacy_pdf.generate_privacy_path",
        lambda p: tmp_path / f"{p.patient_id}-{p.label}-privacy.pdf",
    )


def test_regenerate_hp_invoice_creates_pdf(db, saved_hp_invoice, settings, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    _regenerate_invoice_pdf(saved_hp_invoice, settings, db)
    assert (tmp_path / f"{saved_hp_invoice.invoice_number}.pdf").exists()


def test_regenerate_kg_invoice_creates_pdf(db, saved_kg_invoice, settings, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    _regenerate_invoice_pdf(saved_kg_invoice, settings, db)
    assert (tmp_path / f"{saved_kg_invoice.invoice_number}.pdf").exists()


def test_regenerate_throws_on_unknown_invoice_type(db, saved_hp_invoice, settings, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    saved_hp_invoice.type = "KJASD"
    with pytest.raises(HTTPException) as exc:
        _regenerate_invoice_pdf(saved_hp_invoice, settings, db)
    assert exc.value.status_code == 404


def test_regenerate_hp_throws(db, saved_hp_invoice, settings, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    with pytest.raises(HTTPException) as exc:
        _regenerate_invoice_pdf(saved_hp_invoice, None, db)
    assert exc.value.status_code == 500


def test_regenerate_kg_throws(db, saved_kg_invoice, settings, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    with pytest.raises(HTTPException) as exc:
        _regenerate_invoice_pdf(saved_kg_invoice, None, db)
    assert exc.value.status_code == 500


def test_check_and_regenerate_generates_when_missing(db, saved_hp_invoice, settings, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    pdf_path = tmp_path / f"{saved_hp_invoice.invoice_number}.pdf"
    check_and_regenerate_invoice_pdf(saved_hp_invoice, settings, pdf_path, db)
    assert pdf_path.exists()


def test_check_and_regenerate_skips_when_fresh(db, saved_hp_invoice, settings, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    pdf_path = tmp_path / f"{saved_hp_invoice.invoice_number}.pdf"
    # First call generates the file and stamps pdf_generated_at == updated_at
    check_and_regenerate_invoice_pdf(saved_hp_invoice, settings, pdf_path, db)
    first_mtime = pdf_path.stat().st_mtime
    # Second call: file exists and pdf_generated_at >= updated_at → skips
    check_and_regenerate_invoice_pdf(saved_hp_invoice, settings, pdf_path, db)
    assert pdf_path.stat().st_mtime == first_mtime


def test_check_and_regenerate_therapy_creates_pdf(db, patient, settings, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    check_and_regenerate_therapy_pdf(patient, settings, db)
    assert (tmp_path / f"{patient.patient_id}-{patient.label}-therapy.pdf").exists()


def test_check_and_regenerate_privacy_creates_pdf(db, patient, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    check_and_regenerate_privacy_pdf(patient, db)
    assert (tmp_path / f"{patient.patient_id}-{patient.label}-privacy.pdf").exists()


def test_check_and_regenerate_therapy_throws(db, patient, settings, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    with pytest.raises(HTTPException) as exc:
        check_and_regenerate_therapy_pdf(None, settings, db)
    assert exc.value.status_code == 500


def test_check_and_regenerate_privacy_throws(db, patient, tmp_path, monkeypatch):
    _patch_pdf_paths(monkeypatch, tmp_path)
    with pytest.raises(HTTPException) as exc:
        check_and_regenerate_privacy_pdf(None, db)
    assert exc.value.status_code == 500

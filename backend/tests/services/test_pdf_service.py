from datetime import date

import pytest
from fastapi import HTTPException

from app.models import (
    Gender,
    InvoiceDateDB,
    InvoiceDB,
    InvoiceItemDB,
    InvoiceStatus,
    InvoiceType,
    PatientDB,
    SettingsDB,
)
from app.models.privacyClause_model import PrivacyClauseDB
from app.models.therapyClause_model import TherapyClauseDB
from app.services.pdf_service import (
    _regenerate_invoice_pdf,
    check_and_regenerate_invoice_pdf,
    check_and_regenerate_privacy_pdf,
    check_and_regenerate_therapy_pdf,
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


@pytest.fixture
def patient_female(db):
    p = PatientDB(
        label="FEMTEST",
        first_name="Erika",
        last_name="Musterfrau",
        birthday=date(1985, 6, 15),
        gender=Gender.FEMALE,
        street="Musterstraße",
        street_number="2",
        postal_code="12345",
        city="Berlin",
        kilometers_to_travel=10.0,
        telephone="089-12345",
        email="erika@test.de",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def saved_hp_invoice_female(db, patient_female):
    """HP invoice for a female patient with 2 dates (so last_treatment is set)."""
    inv = InvoiceDB(
        patient_id=patient_female.patient_id,
        invoice_date=date(2026, 1, 15),
        invoice_number="2026-01-15-HP-FEM",
        type=InvoiceType.HP,
        status=InvoiceStatus.SAVED,
        kilometers_at_billing=10.0,
    )
    db.add(inv)
    db.flush()

    d1 = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 1, 10))
    db.add(d1)
    db.flush()
    db.add(InvoiceItemDB(
        invoice_id=inv.invoice_id,
        date_id=d1.date_id,
        description="Behandlung A",
        amount=50.0,
        number="GÖÄ 1",
        quantity=1,
        position=0,
    ))

    d2 = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 1, 17))
    db.add(d2)
    db.flush()
    db.add(InvoiceItemDB(
        invoice_id=inv.invoice_id,
        date_id=d2.date_id,
        description="Behandlung B",
        amount=60.0,
        number="GÖÄ 2",
        quantity=1,
        position=0,
    ))

    db.commit()
    db.refresh(inv)
    return inv


@pytest.fixture
def saved_kg_invoice_female(db, patient_female):
    """KG invoice for a female patient."""
    inv = InvoiceDB(
        patient_id=patient_female.patient_id,
        invoice_date=date(2026, 2, 1),
        invoice_number="2026-02-01-KG-FEM",
        type=InvoiceType.KG,
        status=InvoiceStatus.SAVED,
        kilometers_at_billing=10.0,
    )
    db.add(inv)
    db.flush()

    d1 = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 1, 5))
    d2 = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2026, 1, 12))
    db.add_all([d1, d2])
    db.flush()

    db.add(InvoiceItemDB(
        invoice_id=inv.invoice_id,
        date_id=None,
        description="KG Behandlung",
        amount=30.0,
        number=None,
        quantity=2,
        position=0,
    ))
    db.commit()
    db.refresh(inv)
    return inv


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


# ---------------------------------------------------------------------------
# Female patient — covers gender branches in HP, KG, privacy, therapy PDFs
# ---------------------------------------------------------------------------

def test_regenerate_hp_invoice_female_creates_pdf(
    db, saved_hp_invoice_female, settings, tmp_path, monkeypatch
):
    """Covers invoice_hp_pdf.py lines 92-93 (Frau recipient), 123-124 (Patientin),
    143 (female salutation), 181-191 (last_treatment in dummy), 217-228 (last_treatment actual).
    """
    _patch_pdf_paths(monkeypatch, tmp_path)
    _regenerate_invoice_pdf(saved_hp_invoice_female, settings, db)
    assert (tmp_path / f"{saved_hp_invoice_female.invoice_number}.pdf").exists()


def test_regenerate_kg_invoice_female_creates_pdf(
    db, saved_kg_invoice_female, settings, tmp_path, monkeypatch
):
    """Covers invoice_kg_pdf.py lines 84-85 (Frau), 111-112 (Patientin:), 142 (female salutation)."""
    _patch_pdf_paths(monkeypatch, tmp_path)
    _regenerate_invoice_pdf(saved_kg_invoice_female, settings, db)
    assert (tmp_path / f"{saved_kg_invoice_female.invoice_number}.pdf").exists()


def test_privacy_pdf_female_with_contact_and_clauses(
    db, patient_female, tmp_path, monkeypatch
):
    """Covers privacy_pdf.py lines 50-51 (Frau), 86/88 (telephone/email),
    93-117 (clause rendering with preamble and regular clause).
    """
    _patch_pdf_paths(monkeypatch, tmp_path)
    preamble = PrivacyClauseDB(
        number=0,
        title="Einleitung",
        description="Preamble text here.",
        is_preamble=True,
    )
    clause = PrivacyClauseDB(
        number=1,
        title="Datenschutz",
        description="Erster Abschnitt.\n\nZweiter Abschnitt.",
        is_preamble=False,
    )
    db.add_all([preamble, clause])
    db.commit()
    check_and_regenerate_privacy_pdf(patient_female, db)
    assert (tmp_path / f"{patient_female.patient_id}-{patient_female.label}-privacy.pdf").exists()


def test_therapy_pdf_female_with_contact_and_clauses(
    db, patient_female, settings, tmp_path, monkeypatch
):
    """Covers therapy_pdf.py lines 58-59 (Frau), 93-96 (telephone/email != ''),
    101-119 (clause rendering with price substitution).
    """
    _patch_pdf_paths(monkeypatch, tmp_path)
    clause = TherapyClauseDB(
        number=1,
        title="Honorar",
        description="Preis: {price_from} bis {price_to} Euro.",
    )
    db.add(clause)
    db.commit()
    check_and_regenerate_therapy_pdf(patient_female, settings, db)
    assert (tmp_path / f"{patient_female.patient_id}-{patient_female.label}-therapy.pdf").exists()


# ---------------------------------------------------------------------------
# InvoiceType.GT subheading — covers invoice_pdf.py line 43
# ---------------------------------------------------------------------------

def test_invoice_pdf_gt_sets_gestalttherapeutin_subheading(saved_hp_invoice, settings):
    """Covers invoice_pdf.py line 43: elif invoice.type == InvoiceType.GT.
    InvoicePdf.__init__ sets additional_subheading without calling create_pages,
    so we can instantiate it directly (fonts are available in the test environment).
    """
    from app.pdf.invoice_pdf import InvoicePdf
    from app.models import InvoiceType

    saved_hp_invoice.type = InvoiceType.GT
    pdf = InvoicePdf(saved_hp_invoice, settings)
    assert pdf.additional_subheading == "Gestalttherapeutin"

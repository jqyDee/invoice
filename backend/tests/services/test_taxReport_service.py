from datetime import date

from app.models import InvoiceDateDB, InvoiceDB, InvoiceItemDB, InvoiceStatus, InvoiceType
from app.services.taxReport_service import get_available_years, get_tax_report, get_tax_report_csv


def _paid_invoice(db, patient, invoice_number, invoice_date, paid_at, km=10.0):
    """Helper to insert a fully paid invoice."""
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=invoice_date,
        invoice_number=invoice_number,
        type=InvoiceType.HP,
        status=InvoiceStatus.PAID,
        paid_at=paid_at,
        kilometers_at_billing=km,
    )
    db.add(inv)
    db.flush()

    d = InvoiceDateDB(invoice_id=inv.invoice_id, date=invoice_date)
    db.add(d)
    db.flush()

    db.add(
        InvoiceItemDB(
            invoice_id=inv.invoice_id,
            date_id=d.date_id,
            description="Behandlung",
            amount=80.0,
            number="GÖÄ 1",
            quantity=1,
            position=0,
        )
    )
    db.commit()
    db.refresh(inv)
    return inv


# ---------------------------------------------------------------------------
# get_available_years
# ---------------------------------------------------------------------------


def test_get_available_years_empty(db):
    assert get_available_years(db) == []


def test_get_available_years_with_paid_invoices(db, patient):
    _paid_invoice(db, patient, "2024-01-01-HP-T1", date(2024, 1, 15), date(2024, 6, 1))
    _paid_invoice(db, patient, "2025-01-01-HP-T2", date(2025, 3, 10), date(2025, 7, 20))

    years = get_available_years(db)
    assert 2024 in years
    assert 2025 in years


def test_get_available_years_ordered_descending(db, patient):
    _paid_invoice(db, patient, "2023-01-01-HP-T1", date(2023, 1, 1), date(2023, 6, 1))
    _paid_invoice(db, patient, "2025-01-01-HP-T2", date(2025, 1, 1), date(2025, 6, 1))
    _paid_invoice(db, patient, "2024-01-01-HP-T3", date(2024, 1, 1), date(2024, 6, 1))

    years = get_available_years(db)
    assert years == sorted(years, reverse=True)


def test_get_available_years_excludes_non_paid(db, patient):
    inv = InvoiceDB(
        patient_id=patient.patient_id,
        invoice_date=date(2026, 1, 1),
        invoice_number="2026-01-01-HP-SAVED",
        type=InvoiceType.HP,
        status=InvoiceStatus.SAVED,
    )
    db.add(inv)
    db.commit()

    assert get_available_years(db) == []


# ---------------------------------------------------------------------------
# get_tax_report
# ---------------------------------------------------------------------------


def test_get_tax_report_returns_rows_for_year(db, patient):
    _paid_invoice(db, patient, "2025-03-01-HP-TR", date(2025, 3, 1), date(2025, 9, 1))

    rows = get_tax_report(2025, db)
    assert len(rows) == 1
    row = rows[0]
    assert row.invoice_number == "2025-03-01-HP-TR"
    assert row.invoice_type == InvoiceType.HP
    assert row.paid_date == date(2025, 9, 1)


def test_get_tax_report_excludes_other_years(db, patient):
    _paid_invoice(db, patient, "2024-01-01-HP-T1", date(2024, 1, 15), date(2024, 6, 1))
    _paid_invoice(db, patient, "2025-01-01-HP-T2", date(2025, 3, 10), date(2025, 7, 20))

    rows = get_tax_report(2024, db)
    assert len(rows) == 1
    assert rows[0].paid_date.year == 2024


def test_get_tax_report_empty_year(db, patient):
    _paid_invoice(db, patient, "2025-01-01-HP-T1", date(2025, 1, 1), date(2025, 6, 1))

    rows = get_tax_report(2099, db)
    assert rows == []


def test_get_tax_report_calculates_total(db, patient):
    _paid_invoice(db, patient, "2025-05-01-HP-T1", date(2025, 5, 1), date(2025, 10, 1), km=12.0)

    rows = get_tax_report(2025, db)
    assert rows[0].invoice_total == 80.0  # one item at 80.0


def test_get_tax_report_calculates_travel_distance(db, patient):
    _paid_invoice(db, patient, "2025-06-01-HP-T1", date(2025, 6, 1), date(2025, 11, 1), km=5.0)

    rows = get_tax_report(2025, db)
    # 1 date * 5.0 km * 2 trips = 10.0
    assert rows[0].total_kilometers_travelled == 10.0


def test_get_tax_report_counts_treatment_dates(db, patient):
    inv = _paid_invoice(db, patient, "2025-07-01-HP-T1", date(2025, 7, 1), date(2025, 12, 1))
    # add a second date
    d2 = InvoiceDateDB(invoice_id=inv.invoice_id, date=date(2025, 7, 8))
    db.add(d2)
    db.commit()

    rows = get_tax_report(2025, db)
    assert rows[0].number_of_treatment_dates == 2


# ---------------------------------------------------------------------------
# get_tax_report_csv
# ---------------------------------------------------------------------------


def test_get_tax_report_csv_contains_header(db, patient):
    _paid_invoice(db, patient, "2025-08-01-HP-T1", date(2025, 8, 1), date(2025, 12, 15))
    csv = get_tax_report_csv(2025, db)

    assert "Rechnungsnummer" in csv
    assert "Rechnungstyp" in csv
    assert "Rechnungsbetrag" in csv


def test_get_tax_report_csv_contains_invoice_data(db, patient):
    _paid_invoice(db, patient, "2025-09-01-HP-CSV", date(2025, 9, 1), date(2025, 12, 20))
    csv = get_tax_report_csv(2025, db)

    assert "2025-09-01-HP-CSV" in csv


def test_get_tax_report_csv_empty_year_only_header(db):
    csv = get_tax_report_csv(2099, db)
    lines = [line for line in csv.strip().splitlines() if line]
    assert len(lines) == 1  # only the header row

import csv
import io

from sqlalchemy import extract, select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session

from ..models import InvoiceDB, InvoiceStatus
from ..schemas.taxReport_schema import TaxReportRow


def get_available_years(db: Session) -> list[int]:
    rows = (
        db.query(extract("year", InvoiceDB.paid_at).label("year"))
        .filter(InvoiceDB.status == InvoiceStatus.PAID, InvoiceDB.paid_at.isnot(None))
        .distinct()
        .order_by(extract("year", InvoiceDB.paid_at).desc())
        .all()
    )
    return [int(row.year) for row in rows]


def get_tax_report(year: int, db: Session) -> list[TaxReportRow]:
    stmt = (
        select(InvoiceDB)
        .options(
            joinedload(InvoiceDB.dates),
        )
        .filter(
            InvoiceDB.status == InvoiceStatus.PAID,
            extract("year", InvoiceDB.paid_at) == year,
        )
        .order_by(InvoiceDB.paid_at)
    )

    invoices = db.scalars(stmt).unique().all()

    rows = []
    for inv in invoices:
        assert inv.paid_at is not None  # guaranteed by query filter (paid_at.isnot(None))
        rows.append(
            TaxReportRow(
                invoice_id=inv.invoice_id,
                invoice_number=inv.invoice_number,
                invoice_type=inv.type,
                invoice_date=inv.invoice_date,
                paid_date=inv.paid_at,
                kilometers_at_billing=inv.kilometers_at_billing,
                number_of_treatment_dates=len(inv.dates),
                total_kilometers_travelled=inv.total_travel_distance,
                invoice_total=inv.total,
            )
        )
    return rows


def get_tax_report_csv(year: int, db: Session) -> str:
    rows = get_tax_report(year, db)

    output = io.StringIO()
    with output:
        writer = csv.writer(output)
        writer.writerow(
            [
                "Rechnungsnummer",
                "Rechnungstyp",
                "Rechnungsdatum",
                "Bezahlt am",
                "Km bei Abrechnung",
                "Gesamte Km",
                "Behandlungstermine",
                "Rechnungsbetrag",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.invoice_number,
                    row.invoice_type,
                    row.invoice_date,
                    row.paid_date,
                    row.kilometers_at_billing,
                    row.total_kilometers_travelled,
                    row.number_of_treatment_dates,
                    row.invoice_total,
                ]
            )

        csv_content = output.getvalue()

    return csv_content

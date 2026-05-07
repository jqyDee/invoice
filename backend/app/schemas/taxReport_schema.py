from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models import InvoiceType


class TaxReportItem(BaseModel):
    description: str
    amount: float
    quantity: int
    subtotal: float  # computed: amount * quantity


class TaxReportRow(BaseModel):
    invoice_id: int
    invoice_number: str | None
    invoice_type: InvoiceType
    invoice_date: date
    paid_date: date
    kilometers_at_billing: float | None
    number_of_treatment_dates: int
    total_kilometers_travelled: float
    invoice_total: float

    model_config = ConfigDict(from_attributes=True)

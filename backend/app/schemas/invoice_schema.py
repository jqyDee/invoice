from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

from ..models.invoiceType_enum import InvoiceType
from .invoiceItem_schema import InvoiceItem, InvoiceItemCreate
from .invoiceDate_schema import InvoiceDate, InvoiceDateCreate
from .patient_schema import Patient


class InvoiceBase(BaseModel):
    patient_id: int
    is_draft: bool = True
    invoice_date: date
    type: InvoiceType
    diagnosis: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]
    dates: Optional[List[InvoiceDateCreate]] = None


class InvoiceUpdate(BaseModel):
    patient_id: Optional[int] = None
    is_draft: Optional[bool] = None
    invoice_date: Optional[date] = None
    type: Optional[InvoiceType] = None
    diagnosis: Optional[str] = None

    items: Optional[List[InvoiceItemCreate]] = None
    dates: Optional[List[InvoiceDateCreate]] = None


class Invoice(InvoiceBase):
    invoice_id: int
    # Can be null if it's still a draft
    invoice_number: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    total: float
    items: List[InvoiceItem] = []
    dates: List[InvoiceDate]
    patient: Patient

    class Config:
        from_attributes = True

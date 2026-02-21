from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional, Union

from .defaultInvoiceItem_schema import DefaultInvoiceItemCreate, DefaultInvoiceItem
from ..models import InvoiceStatus
from ..models.invoiceType_enum import InvoiceType
from .invoiceItem_schema import InvoiceItem, InvoiceItemCreate, InvoiceItemUpdate
from .invoiceDate_schema import InvoiceDate, InvoiceDateCreate, InvoiceDateUpdate
from .patient_schema import Patient


class InvoiceBase(BaseModel):
    patient_id: int
    invoice_date: date
    type: InvoiceType
    diagnosis: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    user_items: List[InvoiceItemCreate]
    default_item_ids: List[int] = []
    dates: Optional[List[InvoiceDateCreate]] = None


class InvoiceUpdate(BaseModel):
    patient_id: Optional[int] = None
    invoice_date: Optional[date] = None
    type: Optional[InvoiceType] = None
    diagnosis: Optional[str] = None

    user_items: Optional[List[InvoiceItemUpdate]] = None
    default_item_ids: Optional[List[int]] = None
    dates: Optional[List[InvoiceDateUpdate]] = None


class Invoice(InvoiceBase):
    invoice_id: int
    # Can be null if it's still a draft
    invoice_number: Optional[str] = None
    status: InvoiceStatus
    paid_at: Optional[date] = None

    created_at: datetime
    updated_at: datetime

    total: float
    total_travel_distance: float
    is_locked: bool

    items: List[Union[DefaultInvoiceItem, InvoiceItem]]

    default_items: List[DefaultInvoiceItem]
    user_items: List[InvoiceItemCreate]
    dates: List[InvoiceDate]
    patient: Patient

    class Config:
        from_attributes = True

from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import List, Optional, Union

from .defaultInvoiceItem_schema import DefaultInvoiceItem
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
    user_items: Optional[List[InvoiceItemCreate]] = None
    dates: Optional[List[InvoiceDateCreate]] = None
    default_item_ids: List[int] = []
    save_as_draft: bool = False


class InvoiceMarkPaidRequest(BaseModel):
    paid_at: date


class InvoiceUpdate(BaseModel):
    patient_id: Optional[int] = None
    invoice_date: Optional[date] = None
    type: Optional[InvoiceType] = None
    diagnosis: Optional[str] = None

    user_items: Optional[List[InvoiceItemUpdate]] = None
    default_item_ids: Optional[List[int]] = None
    dates: Optional[List[InvoiceDateUpdate]] = None
    save_as_draft: Optional[bool] = None


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
    user_items: List[InvoiceItem]
    dates: List[InvoiceDate]
    patient: Patient

    @field_validator("default_items", mode="before")
    @classmethod
    def extract_default_items(cls, v):
        if v and hasattr(v[0], "default_item"):
            return [link.default_item for link in v]
        return v

    class Config:
        from_attributes = True

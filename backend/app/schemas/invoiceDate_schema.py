from typing import Optional, List

from pydantic import BaseModel
from datetime import date

from app.schemas import InvoiceItemCreate, InvoiceItemUpdate, InvoiceItem


class InvoiceDateBase(BaseModel):
    date: date


class InvoiceDateCreate(InvoiceDateBase):
    items: Optional[List[InvoiceItemCreate]] = None


class InvoiceDateUpdate(InvoiceDateBase):
    date_id: Optional[int] = None
    items: Optional[List[InvoiceItemUpdate]] = None


class InvoiceDate(InvoiceDateBase):
    date_id: int
    invoice_id: int
    items: List[InvoiceItem] = []

    class Config:
        from_attributes = True

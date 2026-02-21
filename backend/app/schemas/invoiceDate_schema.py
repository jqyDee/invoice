from typing import Optional

from pydantic import BaseModel
from datetime import date


class InvoiceDateBase(BaseModel):
    date: date


class InvoiceDateCreate(InvoiceDateBase):
    pass


class InvoiceDateUpdate(InvoiceDateBase):
    date_id: Optional[int] = None


class InvoiceDate(InvoiceDateBase):
    date_id: int
    invoice_id: int

    class Config:
        from_attributes = True

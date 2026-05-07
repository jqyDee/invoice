from datetime import date

from pydantic import BaseModel, ConfigDict

from .invoiceItem_schema import InvoiceItem, InvoiceItemCreate, InvoiceItemUpdate


class InvoiceDateBase(BaseModel):
    date: date


class InvoiceDateCreate(InvoiceDateBase):
    items: list[InvoiceItemCreate] | None = None


class InvoiceDateUpdate(InvoiceDateBase):
    date_id: int | None = None
    items: list[InvoiceItemUpdate] | None = None


class InvoiceDate(InvoiceDateBase):
    date_id: int
    invoice_id: int
    items: list[InvoiceItem] = []

    model_config = ConfigDict(from_attributes=True)

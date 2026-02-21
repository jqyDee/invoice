from pydantic import BaseModel
from datetime import date as dateType
from typing import Optional


class InvoiceItemBase(BaseModel):
    description: str
    amount: float
    date: Optional[dateType] = None  # Used for HP
    number: Optional[str] = None  # Used for HP
    quantity: int = 1


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemUpdate(InvoiceItemBase):
    item_id: Optional[int] = None


class InvoiceItem(InvoiceItemBase):
    item_id: int
    invoice_id: int

    class Config:
        from_attributes = True

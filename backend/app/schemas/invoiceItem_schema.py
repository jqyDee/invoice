from pydantic import BaseModel
from typing import Optional


class InvoiceItemBase(BaseModel):
    description: str
    amount: float
    number: Optional[str] = None  # Used for HP
    quantity: int = 1


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemUpdate(InvoiceItemBase):
    item_id: Optional[int] = None


class InvoiceItem(InvoiceItemBase):
    item_id: int
    invoice_id: int
    date_id: Optional[int] = None

    class Config:
        from_attributes = True

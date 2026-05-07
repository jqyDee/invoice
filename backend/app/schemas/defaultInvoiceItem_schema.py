from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import DefaultInvoiceItemPosition, InvoiceType


class DefaultInvoiceItemBase(BaseModel):
    description: str
    quantity: Optional[int]
    amount: float
    type: InvoiceType
    number: Optional[str]
    position: DefaultInvoiceItemPosition
    is_active_global: bool

    model_config = ConfigDict(from_attributes=True)


class DefaultInvoiceItem(DefaultInvoiceItemBase):
    default_item_id: int


class DefaultInvoiceItemUpdate(BaseModel):
    description: Optional[str] = None
    quantity: Optional[int] = None
    amount: Optional[float] = None
    type: Optional[InvoiceType] = None
    number: Optional[str] = None
    position: Optional[DefaultInvoiceItemPosition] = None
    is_active_global: Optional[bool] = None


class DefaultInvoiceItemCreate(BaseModel):
    description: str
    amount: float
    type: InvoiceType
    position: DefaultInvoiceItemPosition
    is_active_global: bool
    quantity: Optional[int] = None
    number: Optional[str] = None

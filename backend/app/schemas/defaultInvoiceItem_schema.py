from pydantic import BaseModel, ConfigDict

from app.models import DefaultInvoiceItemPosition, InvoiceType


class DefaultInvoiceItemBase(BaseModel):
    description: str
    quantity: int | None
    amount: float
    type: InvoiceType
    number: str | None
    position: DefaultInvoiceItemPosition
    is_active_global: bool

    model_config = ConfigDict(from_attributes=True)


class DefaultInvoiceItem(DefaultInvoiceItemBase):
    default_item_id: int


class DefaultInvoiceItemUpdate(BaseModel):
    description: str | None = None
    quantity: int | None = None
    amount: float | None = None
    type: InvoiceType | None = None
    number: str | None = None
    position: DefaultInvoiceItemPosition | None = None
    is_active_global: bool | None = None


class DefaultInvoiceItemCreate(BaseModel):
    description: str
    amount: float
    type: InvoiceType
    position: DefaultInvoiceItemPosition
    is_active_global: bool
    quantity: int | None = None
    number: str | None = None

from pydantic import BaseModel, ConfigDict


class InvoiceItemBase(BaseModel):
    description: str
    amount: float
    number: str | None = None  # Used for HP
    quantity: int = 1


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemUpdate(InvoiceItemBase):
    item_id: int | None = None


class InvoiceItem(InvoiceItemBase):
    item_id: int
    invoice_id: int
    date_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

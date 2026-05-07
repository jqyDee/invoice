from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

from ..models import InvoiceStatus
from ..models.invoiceType_enum import InvoiceType
from .defaultInvoiceItem_schema import DefaultInvoiceItem
from .invoiceDate_schema import InvoiceDate, InvoiceDateCreate, InvoiceDateUpdate
from .invoiceItem_schema import InvoiceItem, InvoiceItemCreate, InvoiceItemUpdate
from .patient_schema import Patient


class InvoiceBase(BaseModel):
    patient_id: int
    invoice_date: date
    type: InvoiceType
    diagnosis: str | None = None


class InvoiceCreate(InvoiceBase):
    user_items: list[InvoiceItemCreate] | None = None
    dates: list[InvoiceDateCreate] | None = None
    default_item_ids: list[int] = []
    save_as_draft: bool = False


class InvoiceUpdate(BaseModel):
    patient_id: int | None = None
    invoice_date: date | None = None
    type: InvoiceType | None = None
    diagnosis: str | None = None

    user_items: list[InvoiceItemUpdate] | None = None
    default_item_ids: list[int] | None = None
    dates: list[InvoiceDateUpdate] | None = None
    save_as_draft: bool | None = None


class Invoice(InvoiceBase):
    invoice_id: int
    # Can be null if it's still a draft
    invoice_number: str | None = None
    status: InvoiceStatus
    paid_at: date | None = None

    created_at: datetime
    updated_at: datetime

    kilometers_at_billing: int | None = None
    total: float
    total_travel_distance: float
    is_locked: bool

    items: list[DefaultInvoiceItem | InvoiceItem]

    default_items: list[DefaultInvoiceItem]
    user_items: list[InvoiceItem]
    dates: list[InvoiceDate]
    patient: Patient

    @field_validator("default_items", mode="before")
    @classmethod
    def extract_default_items(cls, v):
        if v and hasattr(v[0], "default_item"):
            return [link.default_item for link in v]
        return v

    model_config = ConfigDict(from_attributes=True)


class PaginatedInvoices(BaseModel):
    items: list[Invoice]
    total: int


class InvoiceMarkPaidRequest(BaseModel):
    paid_at: date


class TemplateItemResponse(BaseModel):
    description: str
    amount: float
    number: str | None = None
    quantity: int = 1
    patient_id: int
    patient_first_name: str
    patient_last_name: str
    invoice_id: int
    invoice_date: date


class DiagnosisTemplateResponse(BaseModel):
    diagnosis: str
    patient_id: int
    patient_first_name: str
    patient_last_name: str
    invoice_id: int
    invoice_date: date


class InvoiceDateGroup(BaseModel):
    date: date
    items: list[InvoiceItemCreate]


class InvoiceTemplateResponse(BaseModel):
    type: InvoiceType
    user_items: list[InvoiceItemCreate] = []
    date_groups: list[InvoiceDateGroup] = []

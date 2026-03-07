from typing import Optional

from sqlalchemy import Enum
from sqlalchemy.sql import expression
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import Base
from .invoiceType_enum import InvoiceType
from .defaultInvoiceItemPosition_enum import DefaultInvoiceItemPosition


class DefaultInvoiceItemDB(Base):
    __tablename__ = "default_invoice_item"

    default_item_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[InvoiceType] = mapped_column(Enum(InvoiceType))
    quantity: Mapped[Optional[int]] = mapped_column()
    description: Mapped[str] = mapped_column()
    amount: Mapped[float] = mapped_column()
    number: Mapped[Optional[str]] = mapped_column()

    is_active_global: Mapped[bool] = mapped_column(server_default=expression.true())

    position: Mapped[DefaultInvoiceItemPosition] = mapped_column(Enum(DefaultInvoiceItemPosition))

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base

if TYPE_CHECKING:
    from .invoice_model import InvoiceDB
    from .invoiceItem_model import InvoiceItemDB


class InvoiceDateDB(Base):
    __tablename__ = "invoice_date"

    date_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoice.invoice_id"))
    date: Mapped[datetime.date] = mapped_column()

    invoice: Mapped[InvoiceDB] = relationship(back_populates="dates")

    # HP
    items: Mapped[list[InvoiceItemDB]] = relationship(
        back_populates="treatment_date", cascade="all, delete-orphan", order_by="InvoiceItemDB.position"
    )

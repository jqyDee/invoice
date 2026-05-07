from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base

if TYPE_CHECKING:
    from .invoice_model import InvoiceDB
    from .invoiceDate_model import InvoiceDateDB


class InvoiceItemDB(Base):
    __tablename__ = "invoice_item"

    item_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoice.invoice_id"))

    number: Mapped[str | None] = mapped_column()
    description: Mapped[str] = mapped_column()
    amount: Mapped[float] = mapped_column()
    quantity: Mapped[int] = mapped_column(default=1)
    position: Mapped[int | None] = mapped_column(default=0)

    invoice: Mapped[InvoiceDB] = relationship(back_populates="user_items")

    # HP
    date_id: Mapped[int | None] = mapped_column(ForeignKey("invoice_date.date_id"))
    treatment_date: Mapped[InvoiceDateDB | None] = relationship(back_populates="items")

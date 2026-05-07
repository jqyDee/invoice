from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base

if TYPE_CHECKING:
    from .defaultInvoiceItem_model import DefaultInvoiceItemDB
    from .invoice_model import InvoiceDB


class InvoiceInvoiceDefaultItemAssociationDB(Base):
    __tablename__ = "invoice_default_item_association"

    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoice.invoice_id"), primary_key=True)
    default_item_id: Mapped[int] = mapped_column(ForeignKey("default_invoice_item.default_item_id"), primary_key=True)

    invoice: Mapped[InvoiceDB] = relationship(back_populates="default_items")
    default_item: Mapped[DefaultInvoiceItemDB] = relationship()

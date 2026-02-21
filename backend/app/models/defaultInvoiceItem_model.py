from sqlalchemy import Column, Integer, String, Float, Enum, Boolean
from sqlalchemy.sql import expression

from .base_model import Base
from .invoiceType_enum import InvoiceType
from .defaultInvoiceItemPosition_enum import DefaultInvoiceItemPosition


class DefaultInvoiceItemDB(Base):
    __tablename__ = "default_invoice_item"

    default_item_id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(InvoiceType), nullable=False)
    quantity = Column(Integer, nullable=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    number = Column(String, nullable=True)

    is_active_global = Column(Boolean, nullable=False, default=True, server_default=expression.true())

    position = Column(Enum(DefaultInvoiceItemPosition), nullable=False)

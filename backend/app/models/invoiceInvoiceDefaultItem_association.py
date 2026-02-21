from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base_model import Base


class InvoiceInvoiceDefaultItemAssociationDB(Base):
    __tablename__ = "invoice_default_item_association"

    invoice_id = Column(Integer, ForeignKey("invoice.invoice_id"), primary_key=True)
    default_item_id = Column(Integer, ForeignKey("default_invoice_item.default_item_id"), primary_key=True)

    invoice = relationship("InvoiceDB", back_populates="default_items")
    default_item = relationship("DefaultInvoiceItemDB")

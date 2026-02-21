from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base_model import Base


class InvoiceItemDB(Base):
    __tablename__ = "invoice_item"

    item_id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoice.invoice_id"), nullable=False)

    date = Column(Date, nullable=True)
    number = Column(String, nullable=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)

    is_internal = Column(Boolean, default=False, nullable=False)

    invoice = relationship("InvoiceDB", back_populates="user_items")

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base_model import Base


class InvoiceItemDB(Base):
    __tablename__ = "invoice_item"

    item_id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoice.invoice_id"), nullable=False)

    number = Column(String, nullable=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)

    invoice = relationship("InvoiceDB", back_populates="user_items")

    # HP
    date_id = Column(Integer, ForeignKey("invoice_date.date_id"), nullable=True)
    treatment_date = relationship("InvoiceDateDB", back_populates="items")

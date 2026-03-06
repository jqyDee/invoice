from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base_model import Base

class InvoiceDateDB(Base):
    __tablename__ = "invoice_date"

    date_id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoice.invoice_id"), nullable=False)
    date = Column(Date, nullable=False)

    invoice = relationship("InvoiceDB", back_populates="dates")

    # HP
    items = relationship("InvoiceItemDB", back_populates="treatment_date", cascade="all, delete-orphan",
                         order_by="InvoiceItemDB.position")
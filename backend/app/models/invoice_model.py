from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .base_model import Base
from .invoiceType_enum import InvoiceType


class InvoiceDB(Base):
    __tablename__ = "invoice"

    invoice_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.patient_id"), nullable=False)

    invoice_number = Column(String, unique=True, index=True, nullable=True)
    invoice_date = Column(Date, nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    pdf_generated_at = Column(DateTime(timezone=True), nullable=True)

    total = Column(Float, default=0.0)

    type = Column(Enum(InvoiceType), nullable=False, default=InvoiceType.KG)
    is_draft = Column(Boolean, default=True, nullable=False)

    diagnosis = Column(Text, nullable=True)

    dates = relationship("InvoiceDateDB", back_populates="invoice", cascade="all, delete-orphan")

    patient = relationship("PatientDB", back_populates="invoices")
    items = relationship("InvoiceItemDB", back_populates="invoice", cascade="all, delete-orphan")
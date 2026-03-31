from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone, date

from sqlalchemy import ForeignKey, Text, Enum, DateTime, select, func, case
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .patient_model import PatientDB
from .invoiceItem_model import InvoiceItemDB
from .invoiceDate_model import InvoiceDateDB
from .invoiceInvoiceDefaultItem_association import InvoiceInvoiceDefaultItemAssociationDB
from .defaultInvoiceItem_model import DefaultInvoiceItemDB
from .defaultInvoiceItemPosition_enum import DefaultInvoiceItemPosition
from .base_model import Base
from .invoiceStatus_enum import InvoiceStatus
from .invoiceType_enum import InvoiceType


class InvoiceDB(Base):
    __tablename__ = "invoice"

    invoice_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.patient_id"))

    invoice_number: Mapped[Optional[str]] = mapped_column(unique=True, index=True)
    invoice_date: Mapped[date] = mapped_column()
    kilometers_at_billing: Mapped[Optional[float]] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    pdf_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    type: Mapped[InvoiceType] = mapped_column(Enum(InvoiceType), default=InvoiceType.KG)
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    paid_at: Mapped[Optional[date]] = mapped_column()

    diagnosis: Mapped[Optional[str]] = mapped_column(Text)

    patient: Mapped[PatientDB] = relationship(back_populates="invoices")

    dates: Mapped[List[InvoiceDateDB]] = relationship(back_populates="invoice", cascade="all, delete-orphan")

    user_items: Mapped[List[InvoiceItemDB]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan", order_by="InvoiceItemDB.position"
    )
    default_items: Mapped[List[InvoiceInvoiceDefaultItemAssociationDB]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )

    @property
    def is_locked(self) -> bool:
        """Logic for locking the invoice."""
        return self.status in [InvoiceStatus.PAYMENT_DUE, InvoiceStatus.PAID]

    @property
    def items(self):
        active_defaults = [link.default_item for link in self.default_items]

        prepend = [d for d in active_defaults if d.position in [
            DefaultInvoiceItemPosition.PREPEND, DefaultInvoiceItemPosition.BOTH
        ]]
        append = [d for d in active_defaults if d.position in [
            DefaultInvoiceItemPosition.APPEND, DefaultInvoiceItemPosition.BOTH
        ]]

        return prepend + self.user_items + append

    @hybrid_property
    def total(self) -> float:
        """Python-level calculation for objects already loaded in memory."""
        date_count = len(self.dates) if self.dates else 1

        # 1. Sum linked default items
        default_total = sum(
            (link.default_item.amount * (
                link.default_item.quantity if link.default_item.quantity is not None else date_count))
            for link in self.default_items
        )

        # 2. Sum manual user items
        user_total = sum((item.amount * item.quantity) for item in self.user_items)

        return round(default_total + user_total, 2)

    @total.expression
    def total(cls):
        """SQL-level calculation for database queries and sorting."""
        # Subquery to determine the date multiplier
        date_count_sub = (
            select(func.count(InvoiceDateDB.date_id))
            .where(InvoiceDateDB.invoice_id == cls.invoice_id)
            .scalar_subquery()
        )

        # If no dates, multiplier is 1
        effective_multiplier = case((date_count_sub == 0, 1), else_=date_count_sub)

        # Subquery for defaults using the date multiplier logic
        default_sum = (
            select(func.sum(
                DefaultInvoiceItemDB.amount * case(
                    (DefaultInvoiceItemDB.quantity.isnot(None), DefaultInvoiceItemDB.quantity),
                    else_=effective_multiplier
                )
            ))
            .select_from(InvoiceInvoiceDefaultItemAssociationDB)
            .join(DefaultInvoiceItemDB)
            .where(InvoiceInvoiceDefaultItemAssociationDB.invoice_id == cls.invoice_id)
            .scalar_subquery()
        )

        # Subquery for user items
        user_sum = (
            select(func.sum(InvoiceItemDB.amount * InvoiceItemDB.quantity))
            .where(InvoiceItemDB.invoice_id == cls.invoice_id)
            .scalar_subquery()
        )

        return func.round(func.coalesce(default_sum, 0) + func.coalesce(user_sum, 0), 2)

    @hybrid_property
    def total_travel_distance(self) -> float:
        """Python-level: Uses the snapshotted km or falls back to current patient data."""
        km_per_trip = self.kilometers_at_billing if self.kilometers_at_billing is not None else (
            self.patient.kilometers_to_travel if self.patient else 0
        )

        multiplier = len(self.dates) if self.dates else 0

        return km_per_trip * multiplier * 2  # as we have 2 trips, to and from

    @total_travel_distance.expression
    def total_travel_distance(cls):
        """SQL-level: Multiplies stored distance (or patient fallback) by date/item count based on type."""
        # Subquery: Count of Dates
        multiplier = (
            select(func.count(InvoiceDateDB.date_id))
            .where(InvoiceDateDB.invoice_id == cls.invoice_id)
            .scalar_subquery()
        )

        effective_km = func.coalesce(
            cls.kilometers_at_billing,
            select(PatientDB.kilometers_to_travel)
            .where(PatientDB.patient_id == cls.patient_id)
            .scalar_subquery()
        )

        return multiplier * effective_km * 2  # as we have 2 trips, to and from

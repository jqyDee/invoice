from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base
from .gender_enum import Gender

if TYPE_CHECKING:
    from .invoice_model import InvoiceDB


class PatientDB(Base):
    __tablename__ = "patient"

    patient_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    label: Mapped[str] = mapped_column(String(4), index=True)  # 4-letter Label

    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    birthday: Mapped[date] = mapped_column()
    gender: Mapped[Gender] = mapped_column(Enum(Gender))

    street: Mapped[str] = mapped_column()
    street_number: Mapped[str] = mapped_column()
    postal_code: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    kilometers_to_travel: Mapped[float] = mapped_column()

    email: Mapped[str | None] = mapped_column()
    telephone: Mapped[str | None] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    invoices: Mapped[list[InvoiceDB]] = relationship(back_populates="patient")

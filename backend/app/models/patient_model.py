from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .gender_enum import Gender
from .base_model import Base

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

    email: Mapped[Optional[str]] = mapped_column()
    telephone: Mapped[Optional[str]] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    invoices: Mapped[List[InvoiceDB]] = relationship(back_populates="patient")

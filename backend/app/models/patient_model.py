from sqlalchemy import Column, Integer, String, Float, Date, Enum, DateTime
from sqlalchemy.orm import relationship

from .gender_enum import Gender
from .base_model import Base
from datetime import datetime


class PatientDB(Base):
    __tablename__ = "patient"

    patient_id = Column(Integer, primary_key=True, index=True)
    label = Column(String(4), index=True)  # 4-letter Label

    first_name = Column(String)
    last_name = Column(String)
    birthday = Column(Date)
    gender = Column(Enum(Gender), nullable=False)

    street = Column(String)
    street_number = Column(String)
    postal_code = Column(String)
    city = Column(String)
    kilometers_to_travel = Column(Float)

    email = Column(String, nullable=True)
    telephone = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.now)

    invoices = relationship("InvoiceDB", back_populates="patient")

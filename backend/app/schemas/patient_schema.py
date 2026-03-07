from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional

from ..models import Gender


class PatientBase(BaseModel):
    label: str
    first_name: str
    last_name: str
    gender: Gender
    street: str
    street_number: str
    postal_code: str
    city: str
    birthday: date
    kilometers_to_travel: float
    email: Optional[str] = None
    telephone: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class Patient(PatientBase):
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True

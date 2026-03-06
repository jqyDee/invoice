from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import PatientDB
from ..schemas import PatientCreate


def load_patient(patient_id: int, db: Session) -> PatientDB:
    patient: Optional[PatientDB] = db.get(PatientDB, patient_id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient konnte nicht gefunden werden.")

    return patient


def perform_create_patient(patient_new: PatientCreate, db: Session) -> PatientDB:
    db_patient = PatientDB(**patient_new.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def perform_update_patient(patient_update: PatientCreate, db_patient: PatientDB, db: Session) -> PatientDB:
    update_data = patient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient

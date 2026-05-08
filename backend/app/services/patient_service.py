from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import InvoiceDB, PatientDB
from ..schemas import PatientCreate


def load_patient(patient_id: int, db: Session) -> PatientDB:
    patient: PatientDB | None = db.get(PatientDB, patient_id)

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


def perform_delete_patient(patient_id: int, db: Session) -> PatientDB:
    existing_invoice = db.scalars(select(InvoiceDB).where(InvoiceDB.patient_id == patient_id)).first()

    if existing_invoice:
        raise HTTPException(status_code=409, detail="Patient hat Rechnungen und kann demnach nicht gelöscht werden.")

    db_patient = load_patient(patient_id, db)

    db.delete(db_patient)
    db.commit()
    return db_patient

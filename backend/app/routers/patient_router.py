from sqlalchemy import or_
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..models import PatientDB
from ..schemas import Patient, PatientCreate
from ..utilities.database import get_db

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=list[Patient])
def get_patients(
        search: Optional[str] = Query(None),  # New search parameter
        db: Session = Depends(get_db)
):
    query = db.query(PatientDB)

    if search:
        # This handles searching "First Last", "Last First", or just parts of either
        # It concatenates first and last name with a space and checks against the search term
        search_filter = or_(
            PatientDB.first_name.ilike(f"%{search}%"),
            PatientDB.last_name.ilike(f"%{search}%"),
            (PatientDB.first_name + " " + PatientDB.last_name).ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    return query.all()

@router.get("/{patient_id}", response_model=Patient)
def get_patient(
        patient_id: str,
        db: Session = Depends(get_db)
):
    return db.query(PatientDB).get(patient_id)

@router.post("/", response_model=Patient)
def create_patient(
        patient_new: PatientCreate,
        db: Session = Depends(get_db)
):
    db_patient = PatientDB(**patient_new.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.delete("/{patient_id}", response_model=Patient)
def delete_patient(
        patient_id: int,
        db: Session = Depends(get_db)
):
    db_patient = db.query(PatientDB).get(patient_id)

    if not db_patient:
        raise HTTPException(status_code=404 , detail="Patient nicht gefunden")

    db.delete(db_patient)
    db.commit()
    return db_patient


@router.put("/{patient_id}", response_model=Patient)
def update_patient(
        patient_id: int,
        patient_update: PatientCreate,
        db: Session = Depends(get_db)
):
    db_patient = db.query(PatientDB).filter(PatientDB.patient_id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404 , detail="Patient nicht gefunden")

    # Update fields from the form data
    update_data = patient_update.model_dump()
    for key, value in update_data.items():
        setattr(db_patient, key, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient

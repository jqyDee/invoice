from sqlalchemy import or_, select
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..models import PatientDB
from ..schemas import Patient, PatientCreate
from ..services.patient_service import load_patient, perform_create_patient, perform_update_patient, \
    perform_delete_patient
from ..utilities.database import get_db

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=list[Patient])
def get_patients(
        search: Optional[str] = Query(None),  # New search parameter
        db: Session = Depends(get_db)
):
    statement = select(PatientDB)

    if search:
        # This handles searching "First Last", "Last First", or just parts of either
        # It concatenates first and last name with a space and checks against the search term
        search_filter = or_(
            PatientDB.first_name.ilike(f"%{search}%"),
            PatientDB.last_name.ilike(f"%{search}%"),
            (PatientDB.first_name + " " + PatientDB.last_name).ilike(f"%{search}%")
        )
        statement = statement.where(search_filter)

    return list(db.scalars(statement).all())


@router.get("/{patient_id}", response_model=Patient)
def get_patient(
        patient_id: int,
        db: Session = Depends(get_db)
):
    return load_patient(patient_id, db)


@router.post("/", response_model=Patient)
def create_patient(
        patient_new: PatientCreate,
        db: Session = Depends(get_db)
):
    return perform_create_patient(patient_new, db)


@router.delete("/{patient_id}", response_model=Patient)
def delete_patient(
        patient_id: int,
        db: Session = Depends(get_db)
):
    return perform_delete_patient(patient_id, db)


@router.put("/{patient_id}", response_model=Patient)
def update_patient(
        patient_id: int,
        patient_update: PatientCreate,
        db: Session = Depends(get_db)
):
    db_patient = load_patient(patient_id, db)
    return perform_update_patient(patient_update, db_patient, db)

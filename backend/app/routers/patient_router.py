from sqlalchemy import or_, select, func
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..models import PatientDB
from ..schemas import Patient, PatientCreate, PaginatedPatients
from ..services.patient_service import load_patient, perform_create_patient, perform_update_patient, \
    perform_delete_patient
from ..utilities.database import get_db
from ..utilities.security import get_current_user

router = APIRouter(prefix="/patients", tags=["patients"], dependencies=[Depends(get_current_user)])


ALLOWED_PATIENT_SORT = {"first_name", "last_name", "created_at", "label"}


@router.get("/", response_model=PaginatedPatients)
def get_patients(
        search: Optional[str] = Query(None),
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=9999),
        sort_field: str = Query("last_name"),
        sort_order: str = Query("asc"),
        db: Session = Depends(get_db)
):
    statement = select(PatientDB)

    if search:
        search_filter = or_(
            PatientDB.first_name.ilike(f"%{search}%"),
            PatientDB.last_name.ilike(f"%{search}%"),
            (PatientDB.first_name + " " + PatientDB.last_name).ilike(f"%{search}%")
        )
        statement = statement.where(search_filter)

    if sort_field in ALLOWED_PATIENT_SORT:
        col = getattr(PatientDB, sort_field)
        statement = statement.order_by(col.desc() if sort_order == "desc" else col.asc())

    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    items = list(db.scalars(statement.offset((page - 1) * size).limit(size)).all())
    return PaginatedPatients(items=[Patient.model_validate(p) for p in items], total=total)


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

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from ..models import SettingsDB
from ..schemas import Settings, SettingsUpdate
from ..utilities.database import get_db

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/", response_model=Settings)
def get_settings(
        db: Session = Depends(get_db)
):
    return db.query(SettingsDB).first()

@router.patch("/", response_model=Settings)
def update_settings(
        settings_update: SettingsUpdate,
        db: Session = Depends(get_db)
):
    db_settings = db.query(SettingsDB).first()

    if db_settings is None:
        db_settings = SettingsDB(**settings_update.model_dump())
        db.add(db_settings)
    else:
        update_data = settings_update.model_dump()
        for key, value in update_data.items():
            setattr(db_settings, key, value)

    db.commit()
    db.refresh(db_settings)
    return db_settings

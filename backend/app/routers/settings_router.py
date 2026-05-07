from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..schemas import Settings, SettingsUpdate
from ..services.settings_service import load_settings, perform_update_settings
from ..utilities.database import get_db
from ..utilities.security import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=Optional[Settings])
def get_settings(db: Session = Depends(get_db)):
    return load_settings(db)


@router.patch("/", response_model=Settings)
def update_settings(settings_update: SettingsUpdate, db: Session = Depends(get_db)):
    db_settings = load_settings(db)
    db_settings = perform_update_settings(db_settings, settings_update, db)

    db.commit()
    db.refresh(db_settings)
    return db_settings

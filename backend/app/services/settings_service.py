from typing import Optional

from sqlalchemy.orm import Session

from app.models import SettingsDB
from app.schemas import SettingsUpdate


def load_settings(db: Session) -> SettingsDB:
    settings: Optional[SettingsDB] = db.query(SettingsDB).first()

    return settings


def perform_update_settings(db_settings: SettingsDB, settings_update: SettingsUpdate, db: Session):
    if db_settings is None:
        db_settings = SettingsDB(**settings_update.model_dump())
        db.add(db_settings)
    else:
        update_data = settings_update.model_dump()
        for key, value in update_data.items():
            setattr(db_settings, key, value)

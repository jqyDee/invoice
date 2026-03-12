import os

from sqlalchemy.orm import Session

from ..models import UserDB
from .security import hash_password


def seed_users(db: Session) -> None:
    username = os.getenv("SEED_USERNAME", "admin")
    password = os.getenv("SEED_PASSWORD", "change-me")

    existing = db.query(UserDB).filter(UserDB.username == username).first()
    if existing is None:
        user = UserDB(username=username, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
    else:
        existing.hashed_password = hash_password(password)
        db.commit()

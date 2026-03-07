from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.privacyClause_model import PrivacyClauseDB
from ..schemas.privacyClause_schema import PrivacyClauseCreate, PrivacyClauseUpdate


def load_privacy_clauses(db: Session) -> list[PrivacyClauseDB]:
    statement = select(PrivacyClauseDB).order_by(PrivacyClauseDB.number)
    return list(db.scalars(statement).all())


def load_privacy_clause(clause_id: int, db: Session) -> PrivacyClauseDB:
    statement = select(PrivacyClauseDB).where(PrivacyClauseDB.clause_id == clause_id)
    clause = db.scalars(statement).first()

    if not clause:
        raise HTTPException(status_code=404, detail="Klausel nicht gefunden.")
    return clause


def create_privacy_clause(data: PrivacyClauseCreate, db: Session) -> PrivacyClauseDB:
    clause = PrivacyClauseDB(**data.model_dump())
    db.add(clause)
    db.commit()
    db.refresh(clause)
    return clause


def update_privacy_clause(clause_id: int, data: PrivacyClauseUpdate, db: Session) -> PrivacyClauseDB:
    clause = load_privacy_clause(clause_id, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(clause, key, value)
    db.commit()
    db.refresh(clause)
    return clause


def delete_privacy_clause(clause_id: int, db: Session) -> None:
    clause = load_privacy_clause(clause_id, db)
    db.delete(clause)
    db.commit()
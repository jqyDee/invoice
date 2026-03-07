from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.therapyClause_model import TherapyClauseDB
from ..schemas.therapyClause_schema import TherapyClauseCreate, TherapyClauseUpdate


def load_clauses(db: Session) -> list[TherapyClauseDB]:
    return list(db.scalars(select(TherapyClauseDB).order_by(TherapyClauseDB.number)).all())


def load_clause(clause_id: int, db: Session) -> TherapyClauseDB:
    clause = db.scalars(select(TherapyClauseDB).where(TherapyClauseDB.clause_id == clause_id)).first()
    if not clause:
        raise HTTPException(status_code=404, detail="Klausel nicht gefunden.")
    return clause


def create_clause(data: TherapyClauseCreate, db: Session) -> TherapyClauseDB:
    clause = TherapyClauseDB(**data.model_dump())
    db.add(clause)
    db.commit()
    db.refresh(clause)
    return clause


def update_clause(clause_id: int, data: TherapyClauseUpdate, db: Session) -> TherapyClauseDB:
    clause = load_clause(clause_id, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(clause, key, value)
    db.commit()
    db.refresh(clause)
    return clause


def delete_clause(clause_id: int, db: Session) -> None:
    clause = load_clause(clause_id, db)
    db.delete(clause)
    db.commit()

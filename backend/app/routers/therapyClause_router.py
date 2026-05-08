from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..schemas import TherapyClause, TherapyClauseCreate, TherapyClauseUpdate
from ..services.therapyClause_service import (
    create_clause,
    delete_clause,
    load_clauses,
    update_clause,
)
from ..utilities.database import get_db
from ..utilities.security import get_current_user

router = APIRouter(prefix="/therapy-clauses", tags=["therapy-clauses"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[TherapyClause])
def get_therapy_clauses(db: Session = Depends(get_db)):
    return load_clauses(db)


@router.post("/", response_model=TherapyClause, status_code=201)
def post_therapy_clause(data: TherapyClauseCreate, db: Session = Depends(get_db)):
    return create_clause(data, db)


@router.patch("/{clause_id}", response_model=TherapyClause)
def patch_therapy_clause(clause_id: int, data: TherapyClauseUpdate, db: Session = Depends(get_db)):
    return update_clause(clause_id, data, db)


@router.delete("/{clause_id}", status_code=204)
def delete_therapy_clause(clause_id: int, db: Session = Depends(get_db)):
    delete_clause(clause_id, db)
    return Response(status_code=204)

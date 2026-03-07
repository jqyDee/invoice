from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..schemas import PrivacyClause, PrivacyClauseCreate, PrivacyClauseUpdate
from ..services.privacyClause_service import (
    load_privacy_clauses,
    create_privacy_clause,
    update_privacy_clause,
    delete_privacy_clause,
)
from ..utilities.database import get_db

router = APIRouter(prefix="/privacy-clauses", tags=["privacy-clauses"])


@router.get("/", response_model=list[PrivacyClause])
def get_privacy_clauses(db: Session = Depends(get_db)):
    return load_privacy_clauses(db)


@router.post("/", response_model=PrivacyClause, status_code=201)
def post_privacy_clause(data: PrivacyClauseCreate, db: Session = Depends(get_db)):
    return create_privacy_clause(data, db)


@router.patch("/{clause_id}", response_model=PrivacyClause)
def patch_privacy_clause(clause_id: int, data: PrivacyClauseUpdate, db: Session = Depends(get_db)):
    return update_privacy_clause(clause_id, data, db)


@router.delete("/{clause_id}", status_code=204)
def delete_privacy_clause_endpoint(clause_id: int, db: Session = Depends(get_db)):
    delete_privacy_clause(clause_id, db)
    return Response(status_code=204)

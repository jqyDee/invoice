from typing import Optional
from pydantic import BaseModel


class TherapyClauseBase(BaseModel):
    number: int
    title: str
    description: str


class TherapyClauseCreate(TherapyClauseBase):
    pass


class TherapyClauseUpdate(BaseModel):
    number: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None


class TherapyClause(TherapyClauseBase):
    clause_id: int

    model_config = {"from_attributes": True}

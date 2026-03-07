from typing import Optional
from pydantic import BaseModel


class PrivacyClauseBase(BaseModel):
    number: int
    title: str
    description: str
    is_preamble: bool


class PrivacyClauseCreate(PrivacyClauseBase):
    pass


class PrivacyClauseUpdate(BaseModel):
    number: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    is_preamble: Optional[bool] = None


class PrivacyClause(PrivacyClauseBase):
    clause_id: int

    model_config = {"from_attributes": True}

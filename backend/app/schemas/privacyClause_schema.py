from pydantic import BaseModel


class PrivacyClauseBase(BaseModel):
    number: int
    title: str
    description: str
    is_preamble: bool


class PrivacyClauseCreate(PrivacyClauseBase):
    pass


class PrivacyClauseUpdate(BaseModel):
    number: int | None = None
    title: str | None = None
    description: str | None = None
    is_preamble: bool | None = None


class PrivacyClause(PrivacyClauseBase):
    clause_id: int

    model_config = {"from_attributes": True}

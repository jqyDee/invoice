from pydantic import BaseModel


class TherapyClauseBase(BaseModel):
    number: int
    title: str
    description: str


class TherapyClauseCreate(TherapyClauseBase):
    pass


class TherapyClauseUpdate(BaseModel):
    number: int | None = None
    title: str | None = None
    description: str | None = None


class TherapyClause(TherapyClauseBase):
    clause_id: int

    model_config = {"from_attributes": True}

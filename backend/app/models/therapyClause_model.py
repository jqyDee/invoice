from sqlalchemy import Column, Integer, String, Text

from .base_model import Base


class TherapyClauseDB(Base):
    __tablename__ = "therapy_clause"

    clause_id   = Column(Integer, primary_key=True, index=True)
    number      = Column(Integer, nullable=False)
    title       = Column(String,  nullable=False)
    description = Column(Text,    nullable=False)

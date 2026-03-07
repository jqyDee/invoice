from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.sql import expression

from .base_model import Base


class PrivacyClauseDB(Base):
    __tablename__ = "privacy_clause"

    clause_id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)  # \n\n = paragraph break
    is_preamble = Column(Boolean, nullable=False, server_default=expression.false())

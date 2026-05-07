from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from .base_model import Base


class PrivacyClauseDB(Base):
    __tablename__ = "privacy_clause"

    clause_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[int] = mapped_column()
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text)  # \n\n = paragraph break
    is_preamble: Mapped[bool] = mapped_column(server_default=expression.false())

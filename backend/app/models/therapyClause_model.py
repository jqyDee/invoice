from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import Base


class TherapyClauseDB(Base):
    __tablename__ = "therapy_clause"

    clause_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[int] = mapped_column()
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text)

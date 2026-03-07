from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from .base_model import Base


class SettingsDB(Base):
    __tablename__ = "settings"

    settings_id: Mapped[int] = mapped_column(primary_key=True)

    iban: Mapped[Optional[str]] = mapped_column()
    bic: Mapped[Optional[str]] = mapped_column()
    tax_id: Mapped[Optional[str]] = mapped_column()

    price_from: Mapped[Optional[float]] = mapped_column(default=100.0)
    price_to: Mapped[Optional[float]] = mapped_column(default=110.0)

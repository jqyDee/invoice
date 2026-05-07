from sqlalchemy.orm import Mapped, mapped_column

from .base_model import Base


class SettingsDB(Base):
    __tablename__ = "settings"

    settings_id: Mapped[int] = mapped_column(primary_key=True)

    iban: Mapped[str | None] = mapped_column()
    bic: Mapped[str | None] = mapped_column()
    tax_id: Mapped[str | None] = mapped_column()

    price_from: Mapped[float | None] = mapped_column(default=100.0)
    price_to: Mapped[float | None] = mapped_column(default=110.0)

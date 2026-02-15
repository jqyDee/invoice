from sqlalchemy import Column, Integer, String, Float
from .base_model import Base

class SettingsDB(Base):
    __tablename__ = "settings"

    settings_id = Column(Integer, primary_key=True)

    iban = Column(String)
    bic = Column(String)
    tax_id = Column(String)

    price_from = Column(Float, default=100.0)
    price_to = Column(Float, default=110.0)

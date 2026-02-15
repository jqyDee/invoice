from pydantic import BaseModel

class SettingsBase(BaseModel):
    iban: str
    bic: str
    tax_id: str
    price_from: float
    price_to: float

class SettingsUpdate(SettingsBase):
    pass

class Settings(SettingsBase):
    id: int

    class Config:
        from_attributes = True
import re

from pydantic import BaseModel, ConfigDict, field_validator


class SettingsBase(BaseModel):
    iban: str
    bic: str
    tax_id: str
    price_from: float
    price_to: float


class SettingsUpdate(SettingsBase):
    @field_validator("iban")
    @classmethod
    def validate_iban(cls, v: str) -> str:
        # Remove spaces and check for German IBAN format (DE + 20 digits)
        v = v.replace(" ", "")
        if not re.match(r"^[A-Z]{2}\d{20}$", v):
            raise ValueError("Ungültiges IBAN-Format (DE + 20 Ziffern erwartet)")
        return v

    @field_validator("bic")
    @classmethod
    def validate_bic(cls, v: str) -> str:
        # BIC is 8 or 11 alphanumeric characters
        v = v.strip().upper()
        if not re.match(r"^[a-zA-Z]{6}[a-zA-Z0-9]{2}([a-zA-Z0-9]{3})?$", v):
            raise ValueError("Ungültiger BIC (8 oder 11 Zeichen erwartet)")
        return v

    @field_validator("tax_id")
    @classmethod
    def validate_tax_id(cls, v: str) -> str:
        # Remove spaces and check for 11-digit Steuer-ID
        v = v.replace(" ", "")
        if not re.match(r"^\d{11}$", v):
            raise ValueError("Ungültige Steuer-ID (11 Ziffern erwartet)")
        return v


class Settings(SettingsBase):
    settings_id: int  # Matches the DB primary key to avoid ResponseValidationError

    model_config = ConfigDict(from_attributes=True)

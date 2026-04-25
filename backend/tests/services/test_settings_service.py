import pytest
from pydantic import ValidationError

from app.schemas.settings_schema import SettingsUpdate
from app.services.settings_service import load_settings, perform_update_settings


def _valid_update(**kwargs) -> SettingsUpdate:
    defaults = dict(
        iban="DE89370400440532013000",
        bic="COBADEFFXXX",
        tax_id="12345678901",
        price_from=90.0,
        price_to=120.0,
    )
    defaults.update(kwargs)
    return SettingsUpdate(**defaults)


# ---------------------------------------------------------------------------
# load_settings
# ---------------------------------------------------------------------------

def test_load_settings_returns_none_when_empty(db):
    result = load_settings(db)
    assert result is None


def test_load_settings_returns_existing(db):
    settings = _valid_update()
    perform_update_settings(None, settings, db)
    db.commit()

    result = load_settings(db)
    assert result is not None
    assert result.iban == "DE89370400440532013000"
    assert result.price_from == 90.0


# ---------------------------------------------------------------------------
# perform_update_settings
# ---------------------------------------------------------------------------

def test_perform_update_settings_creates_when_none(db):
    assert load_settings(db) is None

    perform_update_settings(None, _valid_update(), db)
    db.commit()

    result = load_settings(db)
    assert result is not None
    assert result.bic == "COBADEFFXXX"
    assert result.tax_id == "12345678901"


def test_perform_update_settings_updates_existing(db):
    perform_update_settings(None, _valid_update(price_from=80.0), db)
    db.commit()

    existing = load_settings(db)
    perform_update_settings(existing, _valid_update(price_from=150.0, price_to=200.0), db)
    db.commit()

    result = load_settings(db)
    assert result.price_from == 150.0
    assert result.price_to == 200.0


def test_perform_update_settings_singleton_only_one_record(db):
    perform_update_settings(None, _valid_update(), db)
    db.commit()

    existing = load_settings(db)
    perform_update_settings(existing, _valid_update(price_from=999.0), db)
    db.commit()

    # Only one record should exist
    from sqlalchemy import select
    from app.models import SettingsDB
    count = db.scalar(select(SettingsDB))
    assert count is not None  # exactly one row returned by first()


def test_iban_validation(db):
    with pytest.raises(ValueError):
        _valid_update(iban="Wrong")


def test_bic_validation(db):
    with pytest.raises(ValueError):
        _valid_update(bic="Wrong")


def test_tax_id_validation(db):
    with pytest.raises(ValueError):
        _valid_update(tax_id="Wrong")

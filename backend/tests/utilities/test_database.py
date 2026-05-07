from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import Gender, PatientDB


def _make_patient():
    return PatientDB(
        label="T",
        first_name="A",
        last_name="B",
        birthday=date(1990, 1, 1),
        gender=Gender.MALE,
        street="S",
        street_number="1",
        postal_code="12345",
        city="C",
        kilometers_to_travel=0.0,
    )


def test_get_db_yields_and_closes():
    mock_session = MagicMock()
    with patch("app.utilities.database.SessionLocal", return_value=mock_session):
        from app.utilities.database import get_db
        gen = get_db()
        yielded = next(gen)
        assert yielded is mock_session
        try:
            next(gen)
        except StopIteration:
            pass
    mock_session.close.assert_called_once()


def test_get_db_closes_on_exception():
    mock_session = MagicMock()
    with patch("app.utilities.database.SessionLocal", return_value=mock_session):
        from app.utilities.database import get_db
        gen = get_db()
        next(gen)
        try:
            gen.throw(RuntimeError("forced"))
        except RuntimeError:
            pass
    mock_session.close.assert_called_once()


def test_add_db_returns_item(db):
    from app.utilities.database import add_db
    item = _make_patient()
    result = add_db(item, db)
    assert result.patient_id is not None


def test_add_db_raises_500_on_commit_error(db):
    from app.utilities.database import add_db
    item = _make_patient()
    with patch.object(db, "commit", side_effect=Exception("DB exploded")):
        with pytest.raises(HTTPException) as exc:
            add_db(item, db)
    assert exc.value.status_code == 500
    assert "Datenbankfehler" in exc.value.detail

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_lifespan_calls_seed_users():
    mock_db = MagicMock()
    with patch("app.main.SessionLocal", return_value=mock_db), patch("app.main.seed_users") as mock_seed:
        with TestClient(app):
            pass
    mock_seed.assert_called_once_with(mock_db)
    mock_db.close.assert_called_once()

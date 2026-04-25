import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import UserDB
from app.utilities.database import get_db
from app.utilities.security import create_access_token, hash_password


@pytest.fixture
def client(db):
    """TestClient with get_db overridden to use the in-memory test session."""
    def override_get_db():
        yield db

    user = UserDB(username="testuser", hashed_password=hash_password("testpass"))
    db.add(user)
    db.commit()

    app.dependency_overrides[get_db] = override_get_db
    c = TestClient(app, raise_server_exceptions=True)
    yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """JWT auth headers for testuser (user is created by the client fixture)."""
    token = create_access_token({"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}
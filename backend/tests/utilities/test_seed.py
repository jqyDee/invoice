from app.models import UserDB
from app.utilities.seed import seed_users
from app.utilities.security import verify_password


def test_seed_creates_user_when_absent(db, monkeypatch):
    monkeypatch.setenv("SEED_USERNAME", "seeduser")
    monkeypatch.setenv("SEED_PASSWORD", "seedpass")
    seed_users(db)
    user = db.query(UserDB).filter(UserDB.username == "seeduser").first()
    assert user is not None
    assert verify_password("seedpass", user.hashed_password)


def test_seed_updates_password_when_user_exists(db, monkeypatch):
    monkeypatch.setenv("SEED_USERNAME", "seeduser")
    monkeypatch.setenv("SEED_PASSWORD", "original")
    seed_users(db)
    monkeypatch.setenv("SEED_PASSWORD", "updated")
    seed_users(db)
    user = db.query(UserDB).filter(UserDB.username == "seeduser").first()
    assert verify_password("updated", user.hashed_password)
    assert db.query(UserDB).filter(UserDB.username == "seeduser").count() == 1


def test_seed_uses_defaults(db, monkeypatch):
    monkeypatch.delenv("SEED_USERNAME", raising=False)
    monkeypatch.delenv("SEED_PASSWORD", raising=False)
    seed_users(db)
    assert db.query(UserDB).filter(UserDB.username == "admin").first() is not None

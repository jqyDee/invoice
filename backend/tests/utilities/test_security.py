from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.utilities.security import (
    JWT_ALGORITHM,
    JWT_SECRET,
    create_access_token,
    get_current_user,
)


def test_missing_sub_raises_401(db):
    token = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, db=db)
    assert exc.value.status_code == 401


def test_invalid_token_raises_401(db):
    with pytest.raises(HTTPException) as exc:
        get_current_user(token="not.a.valid.jwt", db=db)
    assert exc.value.status_code == 401


def test_user_not_found_raises_401(db):
    token = create_access_token({"sub": "ghost_user_that_does_not_exist"})
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, db=db)
    assert exc.value.status_code == 401

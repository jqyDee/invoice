from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import UserDB
from ..utilities.database import get_db
from ..utilities.security import create_access_token, get_current_user, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    statement = select(UserDB).where(UserDB.username == form_data.username)
    user = db.scalar(statement)
    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_token(current_user: UserDB = Depends(get_current_user)):
    token = create_access_token(data={"sub": current_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: UserDB = Depends(get_current_user)):
    return {"username": current_user.username}

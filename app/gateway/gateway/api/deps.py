from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from gateway import crud, models, schemas
from gateway.core import security
from gateway.core.config import settings
from gateway.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def getDb() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def getCurrentUser(
    db: Session = Depends(getDb), token: str = Depends(reusable_oauth2)
) -> schemas.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def getCurrentActiveUser(
    current_user: models.User = Depends(getCurrentUser),
) -> schemas.User:
    if not crud.user.isActive(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def getCurrentActiveSuperuser(
    current_user: models.User = Depends(getCurrentUser),
) -> schemas.User:
    if not crud.user.isSuperuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

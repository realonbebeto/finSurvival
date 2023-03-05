from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import crud, models, schemas
from auth.api import deps
from auth.core import security
from auth.core.config import settings

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access(
    db: Session = Depends(deps.getDb), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.isActive(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.createAccessToken(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.getCurrentUser)) -> Any:
    """
    Test access token
    """
    return current_user

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.networks import EmailStr

from gateway import models, schemas
from gateway.api import deps
import requests

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login(user_cred: OAuth2PasswordRequestForm = Depends()
          ) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """

    basicAuth = (user_cred.username, user_cred.password)
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login/access-token", form_data=basicAuth
    )

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        raise HTTPException(
            status_code=400, detail=response.json())
    else:
        raise HTTPException(status_code=500, detail=response.json())


@router.post("/register")
def register(password: str = Body(...),
             email: EmailStr = Body(...),
             full_name: str = Body(None),):
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/open", password=password, email=email, full_name=full_name
    )

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        raise HTTPException(
            status_code=400, detail=response.json())
    else:
        HTTPException(status_code=500, detail=response.json())

from typing import Any

import requests
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.networks import EmailStr

from gateway import schemas
from gateway.core.config import settings

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login(user_cred: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """

    basic_auth = {'username': user_cred.username,
                  'password': user_cred.password}
    response = requests.post(
        f"http://{settings.AUTH_SVC_ADDRESS}/login/access-token", data=basic_auth
    )

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        raise HTTPException(status_code=400, detail=response.json())
    else:
        raise HTTPException(status_code=500, detail=response.json())


@router.post("/register")
def register(
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
):
    user_info = {
        "password": password,
        "email": email,
        "full_name": full_name
    }

    response = requests.post(
        f"http://{settings.AUTH_SVC_ADDRESS}/users/open", json=user_info
    )

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        raise HTTPException(status_code=400, detail=response.json())
    else:
        raise HTTPException(status_code=500, detail=response.json())

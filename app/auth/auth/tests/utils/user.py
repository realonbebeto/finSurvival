from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from auth import crud
from auth.core.config import settings
from auth.models.user import User
from auth.schemas.user import UserCreate, UserUpdate
from auth.tests.utils.utils import randomEmail, randomLowerString


def userAuthenticationHeaders(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def createRandomUser(db: Session) -> User:
    email = randomEmail()
    password = randomLowerString()
    user_in = UserCreate(username=email, email=email, password=password)
    user = crud.user.create(db=db, obj_in=user_in)
    return user


def authenticationTokenFromEmail(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    password = randomLowerString()
    user = crud.user.getByEmail(db, email=email)
    if not user:
        user_in_create = UserCreate(username=email, email=email, password=password)
        user = crud.user.create(db, obj_in=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        user = crud.user.update(db, db_obj=user, obj_in=user_in_update)

    return userAuthenticationHeaders(client=client, email=email, password=password)

from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from auth import crud
from auth.core.config import settings
from auth.schemas.user import UserCreate
from auth.tests.utils.utils import randomEmail, randomLowerString


def testGetUsersSuperuserMe(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


def testGetUsersNormalUserMe(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


def testCreateUserNewEmail(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = randomEmail()
    password = randomLowerString()
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/register",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = crud.user.getByEmail(db, email=username)
    assert user
    assert user.email == created_user["email"]


def testGetExistingUser(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = randomEmail()
    password = randomLowerString()
    user_in = UserCreate(email=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    user_id = user.id
    r = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.user.getByEmail(db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


def testCreateUserExistingUsername(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = randomEmail()
    # username = email
    password = randomLowerString()
    user_in = UserCreate(email=username, password=password)
    crud.user.create(db, obj_in=user_in)
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/register",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


def testCreateUserByNormalUser(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    username = randomEmail()
    password = randomLowerString()
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/register",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 400


def testRetrieveUsers(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = randomEmail()
    password = randomLowerString()
    user_in = UserCreate(email=username, password=password)
    crud.user.create(db, obj_in=user_in)

    username2 = randomEmail()
    password2 = randomLowerString()
    user_in2 = UserCreate(email=username2, password=password2)
    crud.user.create(db, obj_in=user_in2)

    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item

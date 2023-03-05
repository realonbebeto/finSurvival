from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from auth import crud
from auth.core.security import verifyPassword
from auth.schemas.user import UserCreate, UserUpdate
from auth.tests.utils.utils import randomEmail, randomLowerString


def testCreateUser(db: Session) -> None:
    email = randomEmail()
    password = randomLowerString()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def testAuthenticateUser(db: Session) -> None:
    email = randomEmail()
    password = randomLowerString()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db, obj_in=user_in)
    authenticated_user = crud.user.authenticate(db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def testNotAuthenticateUser(db: Session) -> None:
    email = randomEmail()
    password = randomLowerString()
    user = crud.user.authenticate(db, email=email, password=password)
    assert user is None


def testCheckIfUserIsActive(db: Session) -> None:
    email = randomEmail()
    password = randomLowerString()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db, obj_in=user_in)
    is_active = crud.user.isActive(user)
    assert is_active is True


def testCheckIfUserIsActiveInactive(db: Session) -> None:
    email = randomEmail()
    password = randomLowerString()
    user_in = UserCreate(email=email, password=password, disabled=True)
    user = crud.user.create(db, obj_in=user_in)
    is_active = crud.user.isActive(user)
    assert is_active


def testCheckIfUserIsSuperuser(db: Session) -> None:
    email = randomEmail()
    password = randomLowerString()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.user.create(db, obj_in=user_in)
    is_superuser = crud.user.isSuperuser(user)
    assert is_superuser is True


def testCheckIfUserIsNuperuserNormalUser(db: Session) -> None:
    username = randomEmail()
    password = randomLowerString()
    user_in = UserCreate(email=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    is_superuser = crud.user.isSuperuser(user)
    assert is_superuser is False


def testGetUser(db: Session) -> None:
    password = randomLowerString()
    username = randomEmail()
    user_in = UserCreate(email=username, password=password, is_superuser=True)
    user = crud.user.create(db, obj_in=user_in)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def testUpdateUser(db: Session) -> None:
    password = randomLowerString()
    email = randomEmail()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.user.create(db, obj_in=user_in)
    new_password = randomLowerString()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verifyPassword(new_password, user_2.hashed_password)

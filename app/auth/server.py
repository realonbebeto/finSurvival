from datetime import datetime, timedelta, timezone
from typing import *

from models import User, Base
import uvicorn
from database import get_db
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWSError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session


from config import settings
from database import engine, get_db

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRECT_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.token_expire

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

class UserBase(BaseModel):
    email: EmailStr


class CreateUser(UserBase):
    password: str

class UserBase(BaseModel):
    email: EmailStr

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

def hashPwd(password: str):
    return pwd_context.hash(password)


def verify(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)

def createAccessToken(data: dict):
    payload = data.copy()
    # datetime.utcnow()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    iat = datetime.datetime.utcnow()
    payload.update({"exp": expire, "iat": iat})

    encoded = jwt.encode(payload, SECRECT_KEY, algorithm=ALGORITHM)

    return encoded


def verifyAccessToken(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRECT_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception

        token_data = TokenData(id=id)

    except JWSError:
        raise credentials_exception

    return token_data


def getCurrentUser(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verifyAccessToken(token, credentials_exception)

    user = db.query(User).filter(User.id == token.id).first()

    return user


app = FastAPI(title='Authentication')


@app.post("/login", response_model=Token)
def signIn(user_cred: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_cred.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not verify(user_cred.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = createAccessToken(data={"user_id": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def createUser(user: CreateUser, db: Session = Depends(get_db)):

    # Hash the pssword
    hashed_pwd = hashPwd(user.password)
    user.password = hashed_pwd
    user_q = db.query(User).filter_by(email=user.email)

    if user_q.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with email: {user.email} already exists")

    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta, timezone
from app.db import database
from app.models import user_model
from app.models.schema import user_schema, login_schema
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TokenData(BaseModel):
    id: str | None = None



def create_access_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get('user_id')

        if id is None:
            raise credentials_exception
        
        token_data = TokenData(id=id)

    except PyJWTError:
        raise credentials_exception
    

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db:Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate Credentials", headers={'WWW-Authenticate': 'Bearer'})

    token = verify_access_token(token, credentials_exception)

    user = db.query(user_model.User).filter(user_model.User.id == token.id)

    return user


def get_current_active_user(
    current_user: Annotated[user_model.User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
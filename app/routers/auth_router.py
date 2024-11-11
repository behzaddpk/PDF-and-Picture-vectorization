from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.schema.login_schema import UserLoginModel
from app.models.schema.user_schema import UserRegistrationModel
from app.db.database import get_db
from pydantic import BaseModel, EmailStr 
from app.utils.security import hash_password, verify_password
from app.utils.otp_manager import generate_otp, verify_otp, store_otp, remove_otp
from app.models.user_model import User
import secrets
from datetime import datetime
from typing import List, Optional
from app.utils.Oauth import create_access_token


router = APIRouter()

@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegistrationModel, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")

    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"User registered successfully with ID: {new_user.id}")
    return {"message": "User registered successfully.", "user_id": new_user.id}


@router.post("/auth/login")
def login(user: UserLoginModel, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user and verify_password(user.password, db_user.hashed_password):
        access_token = create_access_token(data = {'id': db_user.id})

        return {"message": "Login successful", "session_token": access_token, 'token_type': 'bearer'}
    else:
        print("Incorrect email or password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")


class UserResponseModel(BaseModel):
    id: int
    username: str
    email: str
    registration_date: Optional[datetime]
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True


@router.get("/users/all/", response_model=List[UserResponseModel])
def read_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching users.")

class ForgotPasswordModel(BaseModel):
    email: EmailStr


class ResetPasswordModel(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


@router.post("/auth/forgot-password")
def forgot_password(request: ForgotPasswordModel, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == request.email).first()
    if db_user:
        otp = generate_otp()
        print(f"Generated OTP for {request.email}: {otp}")
        store_otp(request.email, otp)
        return {"message": "OTP sent to your email."}
    else:
        return {"message": "Email not found."}


@router.post("/auth/reset-password")
def reset_password(request: ResetPasswordModel, db: Session = Depends(get_db)):
    if not verify_otp(request.email, request.otp):
        return {"message": "Invalid OTP."}
    db_user = db.query(User).filter(User.email == request.email).first()
    if not db_user:
        return {"message": "User not found."}

    db_user.hashed_password = hash_password(request.new_password)
    db.commit()
    remove_otp(request.email)
    return {"message": "Password updated successfully."}

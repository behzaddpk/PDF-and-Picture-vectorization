from pydantic import BaseModel, EmailStr

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

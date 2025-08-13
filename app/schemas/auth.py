from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    picture: Optional[str]
    provider: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

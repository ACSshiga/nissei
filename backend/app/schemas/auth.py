from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
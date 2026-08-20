from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    email: str | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

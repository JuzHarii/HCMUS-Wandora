from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class SignUpRequest(BaseModel):
    full_name: str = Field(default="Traveler", min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        return normalized or "Traveler"

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str | int | None = None
    email: str | None = None


class UserResponse(BaseModel):
    id: str | int
    email: EmailStr
    full_name: str | None = None
    role: str = "member"
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AuthSessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

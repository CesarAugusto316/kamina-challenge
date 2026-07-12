from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, EmailStr

# avoids circular imports
if TYPE_CHECKING:
    from ..loans.schema import LoanResponse


# --- Base schemas ---
class UserBase(BaseModel):
    name: str
    email: EmailStr


# --- Input schemas ---
class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


# --- Output schemas ---
class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    loans: list["LoanResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# AUTHENTICATION
class JWTRequest(BaseModel):
    email: EmailStr
    password: str


class JWTResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class JWTPayload(BaseModel):
    exp: datetime
    sub: str

    model_config = ConfigDict(from_attributes=True)

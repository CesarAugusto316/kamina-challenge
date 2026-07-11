from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


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


# Forward reference para evitar import circular
class LoanBrief(BaseModel):
    id: int
    loan_date: datetime
    expected_return_date: datetime
    actual_return_date: datetime | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    loans: list[LoanBrief] = []

    model_config = ConfigDict(from_attributes=True)

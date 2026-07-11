from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoanCreate(BaseModel):
    book_id: int
    user_id: int
    days: int | None = None


class LoanUpdate(BaseModel):
    book_id: int | None = None
    user_id: int | None = None
    expected_return_date: datetime | None = None


class LoanResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    loan_date: datetime
    expected_return_date: datetime
    actual_return_date: datetime | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Nested schemas
class UserBrief(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class BookBrief(BaseModel):
    id: int
    title: str
    publication_year: int | None

    model_config = ConfigDict(from_attributes=True)


class AuthorBrief(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class LoanDetailResponse(LoanResponse):
    book: BookBrief
    user: UserBrief

    model_config = ConfigDict(from_attributes=True)


# Para search de libros con author
class BookWithAuthor(BaseModel):
    id: int
    title: str
    publication_year: int | None
    author: AuthorBrief

    model_config = ConfigDict(from_attributes=True)

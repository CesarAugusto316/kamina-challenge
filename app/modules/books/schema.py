from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str
    publication_year: int | None = None
    author_id: int


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    publication_year: int | None = None
    author_id: int | None = None


class BookResponse(BookBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Nested schemas
class AuthorBrief(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class LoanBrief(BaseModel):
    id: int
    loan_date: datetime
    expected_return_date: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class BookDetailResponse(BookResponse):
    author: AuthorBrief
    loans: list[LoanBrief] = []

    model_config = ConfigDict(from_attributes=True)


# Search schema
class BookSearchResponse(BookResponse):
    author: AuthorBrief

    model_config = ConfigDict(from_attributes=True)
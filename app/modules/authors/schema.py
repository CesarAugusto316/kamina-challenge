from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuthorBase(BaseModel):
    name: str
    birth_date: datetime | None = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = None
    birth_date: datetime | None = None


class AuthorResponse(AuthorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Forward reference
class BookBrief(BaseModel):
    id: int
    title: str
    publication_year: int | None

    model_config = ConfigDict(from_attributes=True)


class AuthorDetailResponse(AuthorResponse):
    books: list[BookBrief] = []

    model_config = ConfigDict(from_attributes=True)

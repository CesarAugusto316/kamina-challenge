from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..authors.schema import AuthorResponse


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


# Search schema
class BookSearchResponse(BookResponse):
    author: "AuthorResponse"
    model_config = ConfigDict(from_attributes=True)

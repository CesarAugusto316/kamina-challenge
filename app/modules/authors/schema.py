from datetime import date, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

# avoids circular imports
if TYPE_CHECKING:
    from ..books.schema import BookResponse


class AuthorBase(BaseModel):
    name: str
    # Formato ISO 8601: "YYYY-MM-DD" (ej: "1903-06-25")
    birth_date: date | None = None
    birth_place: str | None = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = None


class AuthorResponse(AuthorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthorDetailResponse(AuthorResponse):
    books: list["BookResponse"] = []

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

# avoids circular imports
if TYPE_CHECKING:
    from ..books.schema import BookResponse


class AuthorBase(BaseModel):
    name: str
    birth_date: datetime | None = (
        None  # manejar formatos como: d/m/y (esto es un formato absoluto, no debe ser UTC)
    )


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = None
    birth_date: datetime | None = None


class AuthorResponse(AuthorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthorDetailResponse(AuthorResponse):
    books: list["BookResponse"] = []

    model_config = ConfigDict(from_attributes=True)

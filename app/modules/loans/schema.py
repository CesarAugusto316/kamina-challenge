from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

# avoids circular imports
if TYPE_CHECKING:
    from ..books.schema import BookResponse
    from ..users.schema import UserResponse


class LoanCreate(BaseModel):
    book_id: int
    # user_id: int
    days: int | None = None


class LoanUpdate(BaseModel):
    days: int | None = None
    # book_id: int | None = None
    # user_id: int | None = None
    # expected_return_date: datetime | None = None


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


class LoanDetailResponse(LoanResponse):
    book: "BookResponse"
    user: "UserResponse"
    model_config = ConfigDict(from_attributes=True)

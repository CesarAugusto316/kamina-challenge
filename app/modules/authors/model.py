from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.db_config import Base

if TYPE_CHECKING:
    from ..books.model import Book


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    birth_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

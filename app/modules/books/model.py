from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.db_config import Base

# avoids circular imports
if TYPE_CHECKING:
    from ..authors.model import Author
    from ..loans.model import Loan


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    publication_year: Mapped[int | None] = mapped_column(nullable=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"), nullable=False
    )

    author: Mapped["Author"] = relationship("Author", back_populates="books")
    loans: Mapped[list["Loan"]] = relationship("Loan", back_populates="book")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

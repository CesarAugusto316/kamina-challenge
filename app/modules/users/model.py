# user.py
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.db_config import Base

# avoids circular imports
if TYPE_CHECKING:
    from ..loans.model import Loan


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        unique=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    loans: Mapped[list["Loan"]] = relationship("Loan", back_populates="user")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

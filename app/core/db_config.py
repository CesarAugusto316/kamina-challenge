from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .vars import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    SQLAlchemy Base class
    docs: https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#whatsnew-20-orm-declarative-typing
    """

    pass


@asynccontextmanager
async def init_db(app: FastAPI):
    """
    This replaces @app.on_event("startup") because is deprecated
    """
    try:
        Base.metadata.create_all(engine)
        yield
    finally:
        # clean up items
        pass


# Get database session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# type for db dependency injection
InjectedDB = Annotated[Session, Depends(get_db_session)]

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from ..core.seeders import seed_database
from .base_model import BaseModel
from .vars import APP_ENV, DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=(APP_ENV == "development"),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Get database session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# type for db dependency injection
InjectedDB = Annotated[Session, Depends(get_db_session)]


@asynccontextmanager
async def init_db(app: FastAPI):
    """
    This replaces @app.on_event("startup") because is deprecated
    """
    try:
        # En desarrollo: create_all (rápido, sin migraciones)
        # En producción: usar Alembic para migraciones
        if APP_ENV in ("development", "test"):
            BaseModel.metadata.create_all(bind=engine)
            print("✓ Database tables created/verified")

            # Seed solo en desarrollo (no en test para mantener tests limpios)
            if APP_ENV == "development":
                db = SessionLocal()
                try:
                    seed_database(db)
                finally:
                    db.close()
        yield
    finally:
        # clean up
        engine.dispose()
        pass

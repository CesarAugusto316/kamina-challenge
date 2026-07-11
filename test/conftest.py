import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db_config import Base, get_db_session
from app.core.vars import TEST_DATABASE_URL
from app.main import app

# Engine y session específicos para tests
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia de DB para usar la base de test"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Aplicar el override a la app
app.dependency_overrides[get_db_session] = override_get_db


@pytest.fixture()
def client():
    """Cliente HTTP para hacer requests a la API"""
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def setup_test_db():
    """Crea tablas antes de cada test y limpia después"""
    Base.metadata.create_all(bind=engine)
    yield
    # Limpieza: borra datos pero mantiene estructura
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture()
def db_session():
    """Acceso directo a la sesión de DB para setup de datos"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

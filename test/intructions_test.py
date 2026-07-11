import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.db_config import Base, engine
from app.main import app

client = TestClient(app)


# 🔁 Setup: crea tablas de test antes de ejecutar
@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)  # Crea tablas si no existen
    yield
    # 👇 Limpieza opcional: borra datos después de cada test
    # with engine.begin() as conn:
    #     conn.execute(Instruction.__table__.delete())


@pytest.fixture
def auth_token() -> str:
    response = client.post(
        "/auth/token", json={"username": "admin", "password": "mindy2026"}
    )
    assert response.status_code in [200, 201]
    access_token = response.json()["access_token"]
    assert isinstance(access_token, str)
    return access_token


# ✅ CASO 1: POST válido → 201 Created
def test_create_instruction_valid(auth_token):
    response = client.post(
        "/instructions/",
        json={"title": "Instrucción de prueba", "content": "Contenido válido"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Instrucción de prueba"
    assert "id" in data  # UUID generado
    assert "created_at" in data


# ❌ CASO 2: POST inválido (title no es string) → 422 Validation Error
def test_create_instruction_invalid_title(auth_token):
    response = client.post(
        "/instructions/",
        json={"title": {"wrong": "type"}, "content": "ok"},  # ❌ debe ser string
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("title" in str(err["loc"]) for err in detail)


# ❌ CASO 3: DELETE con ID inexistente → 404 Not Found
def test_delete_instruction_not_found(auth_token):
    fake_id = str(uuid.uuid4())
    response = client.delete(
        f"/instructions/{fake_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Instruction not found"

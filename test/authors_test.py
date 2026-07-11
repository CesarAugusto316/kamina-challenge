import jwt
import pytest
from fastapi import status

from app.core.vars import JWT_ALGORITHM, JWT_SECRET

# ============================================================
# FIXTURES REUTILIZABLES
# ============================================================


@pytest.fixture()
def user_payload():
    """Payload válido para crear usuario (necesario para autenticación)"""
    return {
        "name": "Auth User",
        "email": "auth@example.com",
        "password": "securepassword123",
    }


@pytest.fixture()
def created_user(client, user_payload):
    """Crea un usuario y lo retorna con su ID extraído del JWT"""
    response = client.post("/users/", json=user_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    # El endpoint retorna solo el JWT. Decodificamos para extraer el ID (sub)
    token = data["access_token"]
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user_id = int(payload["sub"])

    return {**data, "id": user_id}


@pytest.fixture()
def auth_token(client, created_user, user_payload):
    """Obtiene un JWT haciendo login con el usuario creado"""
    response = client.post(
        "/users/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(auth_token):
    """Headers con token de autenticación"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def author_payload():
    """Payload válido para crear autor"""
    return {"name": "George Orwell", "birth_date": "1903-06-25T00:00:00Z"}


# ============================================================
# AUTHENTICATION TESTS
# ============================================================


class TestAuthorAuthentication:
    def test_create_author_unauthenticated(self, client, author_payload):
        """Verifica que no se pueda crear un autor sin token"""
        response = client.post("/authors/", json=author_payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_author_invalid_token(self, client, author_payload):
        """Verifica que no se pueda crear un autor con un token inválido"""
        response = client.post(
            "/authors/",
            json=author_payload,
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================
# CRUD TESTS
# ============================================================


class TestCreateAuthor:
    def test_create_author_success(self, client, auth_headers, author_payload):
        response = client.post("/authors/", json=author_payload, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == author_payload["name"]
        assert "id" in data
        assert "created_at" in data

    def test_create_author_missing_name(self, client, auth_headers):
        """El nombre es obligatorio según el schema AuthorBase"""
        response = client.post(
            "/authors/",
            json={"birth_date": "1903-06-25T00:00:00Z"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestGetAuthors:
    def test_get_all_authors(self, client, auth_headers, author_payload):
        # Crear un autor primero para asegurar que haya al menos uno
        client.post("/authors/", json=author_payload, headers=auth_headers)

        response = client.get("/authors/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_author_by_id(self, client, auth_headers, author_payload):
        # Crear un autor
        create_response = client.post(
            "/authors/", json=author_payload, headers=auth_headers
        )
        author_id = create_response.json()["id"]

        response = client.get(f"/authors/{author_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == author_id
        assert response.json()["name"] == author_payload["name"]

    def test_get_author_not_found(self, client, auth_headers):
        response = client.get("/authors/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateAuthor:
    def test_update_author_success(self, client, auth_headers, author_payload):
        # Crear un autor
        create_response = client.post(
            "/authors/", json=author_payload, headers=auth_headers
        )
        author_id = create_response.json()["id"]

        # Actualizarlo
        response = client.put(
            f"/authors/{author_id}",
            json={"name": "Eric Arthur Blair"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Eric Arthur Blair"

    def test_update_author_not_found(self, client, auth_headers):
        response = client.put(
            "/authors/99999",
            json={"name": "New Name"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteAuthor:
    def test_delete_author_success(self, client, auth_headers, author_payload):
        # Crear un autor
        create_response = client.post(
            "/authors/", json=author_payload, headers=auth_headers
        )
        author_id = create_response.json()["id"]

        # Eliminarlo
        response = client.delete(f"/authors/{author_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar que ya no existe
        get_response = client.get(f"/authors/{author_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_author_not_found(self, client, auth_headers):
        response = client.delete("/authors/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

import jwt
import pytest
from fastapi import status

from app.core.vars import JWT_ALGORITHM, JWT_SECRET

# ============================================================
# FIXTURES REUTILIZABLES
# ============================================================


@pytest.fixture()
def user_payload():
    """Payload válido para crear usuario"""
    return {
        "name": "John Doe",
        "email": "john@example.com",
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

    # Retornamos los datos del token más el ID extraído
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


# ============================================================
# PUBLIC ROUTES
# ============================================================


class TestCreateUser:
    def test_create_user_success(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Ajustado: El endpoint retorna JWTResponse, no los datos del usuario
        assert "access_token" in data
        assert data["token_type"].lower() == "bearer"

    def test_create_user_duplicate_email(self, client, user_payload):
        # Crear primer usuario
        client.post("/users/", json=user_payload)
        # Intentar crear otro con el mismo email
        response = client.post("/users/", json=user_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_create_user_invalid_email(self, client):
        payload = {"name": "Test", "email": "not-an-email", "password": "123"}
        response = client.post("/users/", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_user_missing_required_fields(self, client):
        response = client.post("/users/", json={"name": "Test"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestLogin:
    def test_login_success(self, client, created_user, user_payload):
        response = client.post(
            "/users/login",
            json={"email": user_payload["email"], "password": user_payload["password"]},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"].lower() == "bearer"

    def test_login_wrong_password(self, client, created_user, user_payload):
        response = client.post(
            "/users/login",
            json={"email": user_payload["email"], "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/users/login",
            json={"email": "ghost@example.com", "password": "whatever"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================
# PRIVATE ROUTES
# ============================================================


class TestGetAllUsers:
    def test_get_users_authenticated(self, client, auth_headers, created_user):
        response = client.get("/users/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_users_with_pagination(self, client, auth_headers, created_user):
        response = client.get("/users/?skip=0&limit=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_users_unauthenticated(self, client):
        response = client.get("/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_users_invalid_token(self, client):
        response = client.get(
            "/users/", headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUser:
    def test_get_user_by_id(self, client, auth_headers, created_user):
        user_id = created_user["id"]
        response = client.get(f"/users/{user_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user_id

    def test_get_user_not_found(self, client, auth_headers):
        response = client.get("/users/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateUser:
    def test_update_user_name(self, client, auth_headers, created_user):
        user_id = created_user["id"]
        response = client.put(
            f"/users/{user_id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated Name"

    def test_update_user_email_to_existing(self, client, auth_headers, created_user):
        # Crear otro usuario
        client.post(
            "/users/",
            json={"name": "Other", "email": "other@example.com", "password": "123"},
        ).json()

        # Intentar actualizar el primero con el email del segundo
        response = client.put(
            f"/users/{created_user['id']}",
            json={"email": "other@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteUser:
    def test_delete_user(self, client, auth_headers, created_user):
        user_id = created_user["id"]
        response = client.delete(f"/users/{user_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""

        # Verificar que ya no existe
        get_response = client.get(f"/users/{user_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_user(self, client, auth_headers):
        response = client.delete("/users/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

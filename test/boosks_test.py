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
        "email": "books_auth@example.com",
        "password": "securepassword123",
    }


@pytest.fixture()
def created_user(client, user_payload):
    """Crea un usuario y lo retorna con su ID extraído del JWT"""
    response = client.post("/users/", json=user_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

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
    """Payload válido para crear autor (prerequisito para crear libros)"""
    return {"name": "Gabriel García Márquez", "birth_date": "1927-03-06T00:00:00Z"}


@pytest.fixture()
def created_author(client, auth_headers, author_payload):
    """Crea un autor y lo retorna con su ID"""
    response = client.post("/authors/", json=author_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture()
def book_payload(created_author):
    """Payload válido para crear libro (requiere author_id)"""
    return {
        "title": "Cien años de soledad",
        "publication_year": 1967,
        "author_id": created_author["id"],
    }


# ============================================================
# AUTHENTICATION TESTS
# ============================================================


class TestBookAuthentication:
    def test_create_book_unauthenticated(self, client, book_payload):
        """Verifica que no se pueda crear un libro sin token"""
        response = client.post("/books/", json=book_payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_books_unauthenticated(self, client):
        """Verifica que no se pueda listar libros sin token"""
        response = client.get("/books/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_book_invalid_token(self, client, book_payload):
        """Verifica que no se pueda crear un libro con un token inválido"""
        response = client.post(
            "/books/",
            json=book_payload,
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================
# CRUD TESTS
# ============================================================


class TestCreateBook:
    def test_create_book_success(self, client, auth_headers, book_payload):
        response = client.post("/books/", json=book_payload, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == book_payload["title"]
        assert data["publication_year"] == book_payload["publication_year"]
        assert "id" in data

    def test_create_book_missing_title(self, client, auth_headers, created_author):
        """El título es obligatorio"""
        payload = {"publication_year": 2000, "author_id": created_author["id"]}
        response = client.post("/books/", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_book_invalid_author(self, client, auth_headers):
        """No se puede crear un libro con un author_id inexistente"""
        payload = {
            "title": "Libre fantasma",
            "publication_year": 2020,
            "author_id": 99999,
        }
        response = client.post("/books/", json=payload, headers=auth_headers)
        # Puede retornar 404 (autor no encontrado) o 422 (validación)
        assert response.status_code in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            status.HTTP_400_BAD_REQUEST,
        )


class TestGetBooks:
    def test_get_all_books(self, client, auth_headers, book_payload):
        # Crear un libro primero
        client.post("/books/", json=book_payload, headers=auth_headers)

        response = client.get("/books/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_books_with_pagination(self, client, auth_headers, book_payload):
        client.post("/books/", json=book_payload, headers=auth_headers)

        response = client.get("/books/?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_search_books_by_title(self, client, auth_headers, book_payload):
        client.post("/books/", json=book_payload, headers=auth_headers)

        response = client.get("/books/?title=Cien", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert "Cien" in data[0]["title"]

    def test_search_books_by_author_name(self, client, auth_headers, book_payload):
        client.post("/books/", json=book_payload, headers=auth_headers)

        response = client.get("/books/?author_name=García", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_search_books_by_year(self, client, auth_headers, book_payload):
        client.post("/books/", json=book_payload, headers=auth_headers)

        response = client.get("/books/?year=1967", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["publication_year"] == 1967

    def test_search_books_no_results(self, client, auth_headers, book_payload):
        client.post("/books/", json=book_payload, headers=auth_headers)

        response = client.get("/books/?title=LibroInexistenteXYZ", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_book_by_id(self, client, auth_headers, book_payload):
        create_response = client.post(
            "/books/", json=book_payload, headers=auth_headers
        )
        book_id = create_response.json()["id"]

        response = client.get(f"/books/{book_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == book_id
        assert response.json()["title"] == book_payload["title"]

    def test_get_book_not_found(self, client, auth_headers):
        response = client.get("/books/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateBook:
    def test_update_book_success(self, client, auth_headers, book_payload):
        create_response = client.post(
            "/books/", json=book_payload, headers=auth_headers
        )
        book_id = create_response.json()["id"]

        response = client.put(
            f"/books/{book_id}",
            json={"title": "El amor en los tiempos del cólera"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "El amor en los tiempos del cólera"

    def test_update_book_not_found(self, client, auth_headers):
        response = client.put(
            "/books/99999",
            json={"title": "Nuevo Título"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteBook:
    def test_delete_book_success(self, client, auth_headers, book_payload):
        create_response = client.post(
            "/books/", json=book_payload, headers=auth_headers
        )
        book_id = create_response.json()["id"]

        response = client.delete(f"/books/{book_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar que ya no existe
        get_response = client.get(f"/books/{book_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_book_not_found(self, client, auth_headers):
        response = client.delete("/books/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

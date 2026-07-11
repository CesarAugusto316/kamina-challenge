from datetime import datetime, timedelta, timezone

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
        "name": "Loan User",
        "email": "loan_user@example.com",
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
    """Payload válido para crear autor"""
    return {"name": "J.K. Rowling", "birth_date": "1965-07-31T00:00:00Z"}


@pytest.fixture()
def created_author(client, auth_headers, author_payload):
    """Crea un autor y lo retorna con su ID"""
    response = client.post("/authors/", json=author_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture()
def book_payload(created_author):
    """Payload válido para crear libro"""
    return {
        "title": "Harry Potter and the Philosopher's Stone",
        "publication_year": 1997,
        "author_id": created_author["id"],
    }


@pytest.fixture()
def created_book(client, auth_headers, book_payload):
    """Crea un libro y lo retorna con su ID"""
    response = client.post("/books/", json=book_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture()
def loan_payload(created_book, created_user):
    """Payload válido para crear loan

    Nota: LoanCreate solo acepta book_id, user_id y days (opcional).
    El campo expected_return_date es calculado internamente por el servicio.
    """
    return {
        "book_id": created_book["id"],
        "user_id": created_user["id"],
        "days": 14,
    }


@pytest.fixture()
def created_loan(client, auth_headers, loan_payload):
    """Crea un loan y lo retorna con su ID"""
    response = client.post("/loans/", json=loan_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


# ============================================================
# AUTHENTICATION TESTS
# ============================================================


class TestLoanAuthentication:
    def test_create_loan_unauthenticated(self, client, loan_payload):
        """Verifica que no se pueda crear un loan sin token"""
        response = client.post("/loans/", json=loan_payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_loans_unauthenticated(self, client):
        """Verifica que no se pueda listar loans sin token"""
        response = client.get("/loans/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_loan_invalid_token(self, client, loan_payload):
        """Verifica que no se pueda crear un loan con un token inválido"""
        response = client.post(
            "/loans/",
            json=loan_payload,
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================
# CRUD TESTS
# ============================================================


class TestCreateLoan:
    def test_create_loan_success(self, client, auth_headers, loan_payload):
        response = client.post("/loans/", json=loan_payload, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["book_id"] == loan_payload["book_id"]
        assert data["user_id"] == loan_payload["user_id"]
        assert data["status"] == "active"
        assert "id" in data
        assert "loan_date" in data
        assert "expected_return_date" in data
        assert data["actual_return_date"] is None

    def test_create_loan_invalid_book(self, client, auth_headers, created_user):
        """No se puede crear un loan con un book_id inexistente"""
        payload = {
            "book_id": 99999,
            "user_id": created_user["id"],
            "days": 14,
        }
        response = client.post("/loans/", json=payload, headers=auth_headers)
        assert response.status_code in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_loan_invalid_user(self, client, auth_headers, created_book):
        """No se puede crear un loan con un user_id inexistente"""
        payload = {
            "book_id": created_book["id"],
            "user_id": 99999,
            "days": 14,  # FIX: usar 'days' en lugar de 'expected_return_date'
        }
        response = client.post("/loans/", json=payload, headers=auth_headers)
        assert response.status_code in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_loan_missing_required_fields(self, client, auth_headers):
        """Faltan campos obligatorios"""
        payload = {"book_id": 1}
        response = client.post("/loans/", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestGetLoans:
    def test_get_all_loans(self, client, auth_headers, created_loan):
        response = client.get("/loans/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_loans_with_pagination(self, client, auth_headers, created_loan):
        response = client.get("/loans/?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_active_loans(self, client, auth_headers, created_loan):
        response = client.get("/loans/active", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Todos los loans retornados deben tener status "active"
        for loan in data:
            assert loan["status"] == "active"

    def test_get_loans_by_user(self, client, auth_headers, created_loan, created_user):
        response = client.get(f"/loans/user/{created_user['id']}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Todos los loans deben pertenecer al usuario
        for loan in data:
            assert loan["user_id"] == created_user["id"]

    def test_get_loans_by_book(self, client, auth_headers, created_loan, created_book):
        response = client.get(f"/loans/book/{created_book['id']}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Todos los loans deben ser del libro
        for loan in data:
            assert loan["book_id"] == created_book["id"]

    def test_get_loan_by_id(self, client, auth_headers, created_loan):
        response = client.get(f"/loans/{created_loan['id']}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == created_loan["id"]

    def test_get_loan_not_found(self, client, auth_headers):
        response = client.get("/loans/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestReturnBook:
    def test_return_book_success(self, client, auth_headers, created_loan):
        loan_id = created_loan["id"]
        response = client.put(f"/loans/{loan_id}/return", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "returned"
        assert data["actual_return_date"] is not None

    def test_return_already_returned_book(self, client, auth_headers, created_loan):
        """Intentar retornar un libro ya retornado debería fallar"""
        loan_id = created_loan["id"]
        # Retornar el libro primero
        client.put(f"/loans/{loan_id}/return", headers=auth_headers)
        # Intentar retornarlo de nuevo
        response = client.put(f"/loans/{loan_id}/return", headers=auth_headers)
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT,
        )

    def test_return_nonexistent_loan(self, client, auth_headers):
        response = client.put("/loans/99999/return", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateLoan:
    def test_update_loan_success(self, client, auth_headers, created_loan):
        loan_id = created_loan["id"]
        new_expected_date = (
            datetime.now(timezone.utc) + timedelta(days=30)
        ).isoformat()
        response = client.put(
            f"/loans/{loan_id}",
            json={"expected_return_date": new_expected_date},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        # Verificar que la fecha se actualizó
        updated_loan = response.json()
        assert "expected_return_date" in updated_loan

    def test_update_loan_not_found(self, client, auth_headers):
        response = client.put(
            "/loans/99999",
            json={"expected_return_date": datetime.now(timezone.utc).isoformat()},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

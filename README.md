# 🧠 Kamina Technical Challenge: Library System

## 📖 Description

A modular REST API built with FastAPI, PostgreSQL, SqlAlchemy and Docker to manage a library domain (users, authors, books, and loans). The project follows a domain-oriented architecture, implements JWT-based authentication, and applies clean separation of concerns for scalability and maintainability.

---

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

- Docker & Docker Compose
- _(Optional)_ `uv` or `pip` if running locally without Docker

---

## 🚀 Quick Start

### 1. Clone & Configure Environment

```bash
cp .env.example .env
```

The `.env` file contains all required configuration (database, JWT, environment). Default values work for local development.

---

### 2. Start the Application

Start app containers

```bash
docker compose --profile app up -d
```

Stop app containers

```bash
docker compose --profile app down
```

✅ API: http://localhost:8000

📖 Docs: http://localhost:8000/docs

### 3. Running Integration Tests

Start test containers, run integration tests, then stop test containers (one command)

```bash
docker compose --profile test up --abort-on-container-exit
```

---

## 🔐 Authentication & Usage Guide

This API uses JWT for authentication.

### 🔑 Create a User

```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{ "name": "John Doe", "email": "user@example.com", "password": "mysecret"}'
```

### Login

```bash
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{ "email": "user@example.com", "password": "mysecret"}'
```

Response:

```json
{
  "access_token": "TOKEN",
  "token_type": "bearer"
}
```

---

### 🛡️ Use Token

```bash
-H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🌐 API Overview

### Core Endpoints

| Method | Endpoint     | Auth | Description |
| ------ | ------------ | ---- | ----------- |
| POST   | /users       | ❌   | Create user |
| POST   | /users/login | ❌   | Login       |

---

### Users

| Method | Endpoint | Auth | Description |
| ------ | -------- | ---- | ----------- |
| GET    | /users   | ✅   | List users  |

---

### Authors

| Method | Endpoint | Auth | Description   |
| ------ | -------- | ---- | ------------- |
| GET    | /authors | ✅   | List authors  |
| POST   | /authors | ✅   | Create author |

---

### Books

| Method | Endpoint | Auth | Description |
| ------ | -------- | ---- | ----------- |
| GET    | /books   | ✅   | List books  |
| POST   | /books   | ✅   | Create book |

---

### Loans

| Method | Endpoint      | Auth | Description   |
| ------ | ------------- | ---- | ------------- |
| GET    | /loans        | ✅   | List loans    |
| POST   | /loans        | ✅   | Create loan   |
| POST   | /loans/return | ✅   | Return a book |

---

## 🧱 Domain Model Overview

- **User** → system users (authentication & ownership)
- **Author** → book authors
- **Book** → individual book units (1 record = 1 copy)
- **Loan** → borrowing lifecycle (loan_date, due_date, return_date)

---

## 📁 Project Structure

```
kamina-challenge/
├── README.md
├── app/
│   ├── main.py               # FastAPI entrypoint
│   ├── core/                 # Shared infrastructure
│   │   ├── db_config.py      # DB configuration
│   │   └── vars.py           # Environment variables
│   │
│   └── modules/              # Domain-based modular architecture
│       ├── users/
│       │   ├── model.py
│       │   ├── schema.py
│       │   ├── service.py
│       │   └── router.py
│       │
│       ├── authors/
│       ├── books/
│       ├── loans/
│       │   ├── model.py      # Loan entity (loan_date, return_date, etc.)
│       │   ├── schema.py
│       │   ├── service.py    # Business rules (availability, return logic)
│       │   └── router.py
│
├── docker-compose.yml
├── dockerfile
├── pyproject.toml
├── test/
│   └── users_test.py
└── uv.lock
```

---

## 🧠 Architectural Notes

- **Modular monolith**: each domain encapsulates model, schema, service, and router
- **Separation of concerns**:

  - Router → HTTP layer
  - Service → business logic
  - Model → persistence
  - Schema → validation

- **Scalable structure**: easy to extract modules into microservices if needed
- **Domain-driven approach**: reflects real-world entities (books, loans, users)

---

## 🚀 Key Design Decisions

- Loans modeled explicitly to handle lifecycle (loan, return, overdue)
- One book = one unit (simplifies inventory constraints)
- JWT-based authentication
- Modular structure for scalability and clarity
- Integration tests using a real database (no mocks)

### Additional Considerations

- **Role-based access (intentionally simplified)**
  The system currently does not implement role-based authorization to keep the challenge focused and concise. However, in a production scenario, at least two roles would be required:

  - **Admin** → responsible for managing authors and books
  - **User** → allowed to browse and borrow books
    This separation is important to enforce proper access control and prevent unauthorized modifications to core domain entities.

- **Isolated test environment with Docker**
  The testing setup uses a dedicated Docker profile with an independent database and test runner container. Each test run operates on an isolated environment, ensuring reproducibility and avoiding side effects between executions.

- **Integration testing over mocking**
  Instead of mocking services or database interactions, tests are executed against a real PostgreSQL instance. This approach aligns with modern CI/CD practices, where reliability and realistic system behavior are prioritized over isolated unit assumptions.

- **Ephemeral infrastructure mindset**
  Test containers are designed to be short-lived: they are created for the test run and destroyed afterward. This mirrors real-world CI pipelines and guarantees consistent, clean states for every execution.

- **Separation between application and testing contexts**
  The architecture clearly distinguishes between application services (`api`, `db`) and testing services (`test_runner`, `test_db`), allowing the system to scale testing strategies independently from application deployment.

---

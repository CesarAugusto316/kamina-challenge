# 🧠 Kamina Technical Test: Library System

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

### 3. Running Integration Tests

Start test containers, run integration tests, then stop test containers

```bash
docker compose --profile test up --abort-on-container-exit
```

✅ API: http://localhost:8000
📖 Docs: http://localhost:8000/docs

---

## 🔐 Authentication & Usage Guide

This API uses JWT for authentication.

### 🔑 Get Token

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "mindy2026"}'
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
| POST   | /users/login | ❌   | Login       |

---

### Users

| Method | Endpoint | Auth | Description |
| ------ | -------- | ---- | ----------- |
| GET    | /users   | ✅   | List users  |
| POST   | /users   | ✅   | Create user |

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
├── ARCHITECTURE_EVOLUTION.md
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
│   └── intructions_test.py
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

## Testing Approach

Instead of relying on mocks for APIs, services, or database interactions, tests are implemented as integration tests running against a real testing database. This approach better reflects real-world behavior and is widely adopted in modern backend development, particularly within continuous integration and deployment pipelines. In typical CI/CD workflows (e.g., GitHub Actions), these tests are executed automatically before critical steps such as merging into main branches or deploying to staging/production environments. By validating the system end-to-end, this strategy provides stronger guarantees that the API behaves as expected under realistic conditions, reducing the risk of inconsistencies that often arise from heavily mocked unit tests.

```
    Developer → Push / PR
              ↓
        CI Pipeline
              ↓
      Docker Compose
      (API + Test DB)
              ↓
      Run Integration Tests
        (real database)
              ↓
        ┌───────────────┐
        │ Tests Pass?   │
        └──────┬────────┘
                │
        Yes ───┴─── No
          ↓            ↓
    Merge / Deploy   Stop
          ↓
    Tear Down Containers
```

---

## 🚀 Key Design Decisions

- Loans modeled explicitly to handle lifecycle (loan, return, overdue)
- One book = one unit (simplifies inventory constraints)
- JWT-based authentication
- Modular structure for scalability and clarity
- Integration tests 100% covered

---

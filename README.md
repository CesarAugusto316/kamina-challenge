# 🧠 Kamina Technical Test

## 📖 Description
A lightweight REST API built with FastAPI, PostgreSQL, and Docker to manage AI assistant instructions. It implements JWT-based authentication, CRUD operations, and follows modern backend architecture patterns.

## 📋 Prerequisites
Before running the project, ensure you have the following installed:
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- *(Optional)* `uv` or `pip` if you prefer running locally without Docker.

## 🚀 Quick Start

### 1. Clone & Configure Environment
```bash
cp .env.example .env
```
The `.env` file contains all necessary configuration (database URL, JWT secret, environment mode). Default values work out-of-the-box for local development.

### 2. Start the Application
Run the following command to spin up the FastAPI app and PostgreSQL database:
```bash
# start docker container
docker compose up -d

# kill docker container
docker compose down

# Rebuild if some file changes
docker compose build --no-cache
```

✅ API: `http://localhost:8000`
📖 Interactive Docs: `http://localhost:8000/docs`

---

## 🔐 Authentication & Usage Guide

This API uses JWT (JSON Web Tokens) to protect routes. Follow these simple steps to authenticate and use the protected endpoints:

### 🔑 Step 1: Obtain a JWT Token
Send a `POST` request to `/auth/token` with the test credentials:
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "mindy2026"}'
```
**You will receive:**
```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }
```
Copy the value inside `"access_token"`.

### 🛡️ Step 2: Use the Token on Protected Routes
Add the token to the `Authorization` header using the `Bearer` scheme.

**📥 List Instructions**
```bash
curl -X GET http://localhost:8000/instructions \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**📝 Create an Instruction**
```bash
curl -X POST http://localhost:8000/instructions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{"title": "Be helpful", "content": "Always answer clearly and concisely."}'
```

**🗑️ Delete an Instruction**
```bash
curl -X DELETE http://localhost:8000/instructions/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 💡 Easier Alternative: Swagger UI
1. Open `http://localhost:8000/docs` in your browser.
2. Click the **"Authorize"** button (top-right 🔓 icon).
3. Paste your token in this format: `Bearer <YOUR_TOKEN>`
4. Click **Authorize** → Close.
5. All protected endpoints will now automatically include your token when testing.

---

## 🌐 API Endpoints

| Method | Endpoint | Auth | Description |
|:------:|:--------:|:----:|-------------|
| `GET`  | `/health` | ❌ | Service health check |
| `POST` | `/auth/token` | ❌ | Login & get JWT |
| `GET`  | `/instructions` | ✅ | List all instructions |
| `POST` | `/instructions` | ✅ | Create a new instruction |
| `DELETE`| `/instructions/{id}` | ✅ | Delete instruction by UUID |

---

## 📁 Project Structure
```
    mindy-task/
    ├── README.md
    ├── app/
    │   ├── __init__.py
    │   ├── core/          # DB config, dependencies, env vars
    │   ├── main.py        # FastAPI entry point
    │   ├── models/        # SQLAlchemy models
    │   ├── routes/        # FastAPI routers (auth, health, instructions)
    │   ├── schemas/       # Pydantic validation models
    │   └── services/      # Auth logic & business helpers
    ├── docker-compose.yml
    ├── dockerfile
    ├── pyproject.toml
    ├── test/              # Pytest suite
    └── uv.lock
```
*(Note: `__pycache__/` and `.venv/` directories are auto-generated and ignored by Git.)*

---

## 🧪 Running Tests
Tests are located in the `test/` directory. Run them inside the container:
```bash
docker compose exec api uv run pytest test/ -v
```

## 📝 Notes for Evaluators
- Hardcoded credentials for testing: `username: admin` / `password: mindy2026`
- All timestamps and JWT expirations use UTC.
- Database tables are auto-created on startup via SQLAlchemy.
- No production secrets are committed. Use `.env.example` as a template.

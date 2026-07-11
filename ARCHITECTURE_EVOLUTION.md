
# 🏗️ Architecture Overview

This document describes the current architecture of the `mindy-task` backend, its planned evolution toward a modular structure, and the principles guiding technical decisions to maintain the balance between **development speed, maintainability, and scalability**.

## 📐 Current Architecture: Layered Approach (Horizontal)

Currently, the project follows a **technical layer-based architecture**:
```
app/
├── routes/        # Endpoints (FastAPI Routers)
├── schemas/       # Input/output validation (Pydantic)
├── models/        # ORM mapping (SQLAlchemy)
├── services/      # Business logic & utilities
└── core/          # Configuration, DB, shared dependencies
```

✅ **Advantages:**
- Fast to implement for small projects or technical tests.
- Clear separation of technical responsibilities.
- Easy for new developers to understand.

⚠️ **Limitations as it scales:**
- Files related to the same domain (e.g., `instructions`) get scattered across multiple folders.
- Makes clear feature ownership difficult (`"Where do I change the logic for endpoint X?"`).
- Increases friction when adding feature-specific tests, migrations, or middleware.

---

## 🧱 Proposed Architecture: Modular / Feature-Based (Vertical Slicing)

The recommended natural evolution is a **domain/feature-centric modular architecture**, inspired by the **NestJS** module pattern and widely adopted in modern FastAPI projects.

Instead of grouping by file type, we group **everything related to a feature into a single folder**:

```
app/
├── core/                 # Shared utilities (DB, config, security, base deps)
├── modules/
│   ├── auth/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── tests/
│   ├── instructions/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── deps.py
│   │   └── tests/
│   └── agents/           # (Future)
│       ├── router.py
│       ├── schemas.py
│       └── service.py
└── main.py
```

### 🔍 Why this approach?
| Criteria | Layered Approach | Modular Approach |
|----------|------------------|------------------|
| **Cohesion** | Low (scattered files) | High (everything feature-related together) |
| **Onboarding** | Requires understanding the entire structure | Can be understood module by module |
| **Scalability** | Becomes fragile >5 endpoints | Grows linearly without massive refactoring |
| **Testing** | Tests mixed by layer | Tests isolated by domain |
| **Real-world coverage** | 50-60% of production scenarios | **70-80%** of typical AI/Agent API cases |

---

## 🎯 Scenarios Covered by This Architecture

FastAPI at MindyCore is primarily used for:
- Exposing APIs for instruction/prompt management.
- Orchestrating calls to LLMs or external agents.
- Simple authentication, webhooks, logging, and metrics.
- CRUD operations with strict validation and typed responses.

This modular structure covers **the vast majority of these cases** because:
1. Each module is **self-contained** regarding validation, persistence, and HTTP exposure.
2. Complex logic is encapsulated in `service.py`, keeping routers thin.
3. `core/` centralizes shared infrastructure (DB pool, JWT, config, logging).
4. Circular dependencies are avoided through explicit dependency injection (`Depends()`).

---

## 🔄 Natural Evolution Path

| Phase | Architecture | When to Apply |
|-------|--------------|---------------|
| **1️⃣ Current** | Horizontal Layers | MVPs, technical tests, < 10 endpoints |
| **2️⃣ Next** | Modular / Feature-based | > 3 domains, team > 2 devs, need for isolated testing |
| **3️⃣ Future** | DDD / Hexagonal | Complex transactional logic, multiple bounded contexts, integration with legacy systems or microservices |

💡 **Golden Rule:** Do not introduce DDD or Hexagonal Architecture unless business complexity justifies it. For agent/LLM management APIs, modular architecture offers **the best balance between speed, clarity, and maintainability**.

---

## 🛡️ Principles for Keeping the Architecture Clean

1. **Decoupled modules:** A module should never import directly from another. If logic needs to be reused, extract it to `core/` or create an explicit interface.
2. **Thin routers:** Validation → Service → Database. Avoid business logic in `router.py`.
3. **Strict schemas:** Use Pydantic v2. `InstructionCreate` for input, `InstructionResponse` for output. Never expose ORM models directly.
4. **Explicit dependencies:** Use `Depends()` for DB, auth, and validation. Avoid global variables or circular imports.
5. **Module-level tests:** Each `modules/feature/` folder should include its own `tests/`. Run with `pytest modules/feature/tests/`.

---

## 🤝 Conclusion

This architecture is designed to **scale without over-engineering**. It covers 70-80% of real-world cases MindyCore faces when developing APIs for AI agents, maintaining the delivery speed required in a startup environment, while providing enough structure to keep the code readable, testable, and maintainable long-term.

When business logic becomes significantly more complex (multi-step workflows, compensations, multiple bounded contexts), the modular foundation will allow a smooth transition to more advanced patterns (DDD/Hexagonal) without requiring a rewrite from scratch.

---

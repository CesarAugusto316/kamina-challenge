from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .core.db import create_db_and_tables
from .core.vars import origins

# from .routes import auth, health, instructions

# Importar modelos para que Base los registre
app = FastAPI(title="Kamina Technical Challenge", lifespan=create_db_and_tables)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(health.router)
# app.include_router(auth.router)
# app.include_router(instructions.router)

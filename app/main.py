from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .core.db_config import init_db
from .core.vars import ALLOWED_ORIGIN
from .modules.authors.router import router as author_router
from .modules.books.router import router as book_router
from .modules.loans.router import router as loan_router
from .modules.users.router import router as user_router

# Importar modelos para que Base los registre
app = FastAPI(
    title="Kamina Library System",
    lifespan=init_db,
    summary="For managing authors, books, and loans",
    description="Get JWT token then use it to access protected endpoints",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(author_router)
app.include_router(book_router)
app.include_router(loan_router)

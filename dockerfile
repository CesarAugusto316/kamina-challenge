FROM ghcr.io/astral-sh/uv:0.11.10-python3.13-trixie

WORKDIR /app

# Copiar metadata e instalar dependencias en capa cacheable
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copiar código fuente
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

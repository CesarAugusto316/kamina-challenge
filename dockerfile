FROM ghcr.io/astral-sh/uv:0.11.10-python3.13-trixie

WORKDIR /app

COPY pyproject.toml uv.lock ./
# Sin --no-dev para que instale pytest del grupo dev
RUN uv sync --frozen

COPY . .

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

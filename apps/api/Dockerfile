FROM ghcr.io/astral-sh/uv:0.12.17 AS uv
FROM python:3.12-slim-bookworm
COPY --from=uv /uv /uvx /bin/
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1
WORKDIR /app/apps/api
COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY apps/api/src ./src
RUN useradd --uid 10001 --create-home horizon
USER horizon
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD ["/app/apps/api/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=3)"]
CMD ["uv", "run", "--no-sync", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

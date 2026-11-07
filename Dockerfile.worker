FROM debian:bookworm-slim AS engine
RUN apt-get update && apt-get install -y --no-install-recommends cmake g++ make && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY engine ./engine
RUN cmake -S engine -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j2 && ctest --test-dir build --output-on-failure

FROM ghcr.io/astral-sh/uv:0.12.17 AS uv
FROM python:3.12-slim-bookworm
COPY --from=uv /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 QUANT_ENGINE_PATH=/app/bin/horizon_quant
WORKDIR /app/workers
COPY workers/pyproject.toml workers/uv.lock ./
RUN uv sync --frozen --no-dev
COPY workers ./
COPY --from=engine /src/build/horizon_quant /app/bin/horizon_quant
RUN useradd --uid 10001 --create-home horizon
USER horizon
HEALTHCHECK --interval=60s --timeout=10s --start-period=90s CMD ["/app/workers/.venv/bin/python", "-m", "core.health"]
CMD ["uv", "run", "--no-sync", "python", "-m", "core.run"]

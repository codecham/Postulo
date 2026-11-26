# syntax=docker/dockerfile:1

# --- Build stage: install the dependencies into /code/.venv with uv ---
FROM python:3.15-slim AS build

COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /code
# Only the lock files: this layer stays cached until the dependencies change
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# --- Runtime stage (production): no uv, no build tools, no dev dependencies ---
FROM python:3.15-slim AS runtime

ENV PATH="/code/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# The cache folder is owned by "app", so the volume mounted there (embedding model) is writable
RUN useradd --create-home --uid 1000 app \
    && mkdir -p /home/app/.cache/huggingface \
    && chown -R app:app /home/app/.cache
WORKDIR /code

# The code belongs to root and is only readable by "app": a compromised process
# cannot change the code it runs
COPY --from=build /code/.venv ./.venv
COPY alembic.ini ./
COPY migrations ./migrations
COPY scripts ./scripts
COPY app ./app

USER app
EXPOSE 8000

# One process: the login rate limiter keeps its counts in memory (see DEPLOY.md).
# --proxy-headers reads the client IP from X-Forwarded-For, trusted only from the
# addresses in FORWARDED_ALLOW_IPS (127.0.0.1 unless the container sets it).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

# --- Development stage: same image, code owned by "app" so `docker compose watch`
# can sync edited files into the container (compose.override.yaml picks this target) ---
FROM runtime AS dev
USER root
RUN chown -R app:app /code/app /code/migrations /code/scripts
USER app

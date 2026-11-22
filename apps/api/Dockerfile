FROM python:3.15-slim

COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /usr/local/bin/uv

WORKDIR /code

ENV PATH="/code/.venv/bin:$PATH"
RUN useradd --create-home appuser

# Dependencies first: this layer stays cached until uv.lock changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Application code last: it changes most often
COPY app ./app

# Drop root privileges only for running the app
USER appuser

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]

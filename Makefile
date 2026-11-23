.PHONY: help up down logs test check migration migrate rollback db-status db-shell web-dev web-check
.DEFAULT_GOAL := help

API := apps/api

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# --- Docker ---
up: ## Start everything (dev mode, auto-reload)
	docker compose up -d --build

down: ## Stop everything (data is kept)
	docker compose down

logs: ## Follow the API logs
	docker compose logs -f api

# --- Quality ---
test: ## Run the tests
	cd $(API) && uv run pytest

check: ## Run all checks: API (tests, types, lint) and web (before each commit)
	cd $(API) && uv run pytest && uv run mypy app tests && uv run ruff check .
	$(MAKE) web-check

# --- Database ---
migration: ## Create a migration: make migration m="add avatar to users"
	@test -n "$(m)" || (echo 'Missing message: make migration m="describe the change"' && exit 1)
	cd $(API) && uv run alembic revision --autogenerate -m "$(m)"

migrate: ## Apply all pending migrations
	cd $(API) && uv run alembic upgrade head

rollback: ## Undo the last migration
	cd $(API) && uv run alembic downgrade -1

db-status: ## Show the current migration and the history
	cd $(API) && uv run alembic current && uv run alembic history

db-shell: ## Open a psql console on the database
	docker compose exec db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

# --- Web ---
web-dev: ## Start the Next.js dev server on http://localhost:3000
	cd apps/web && npm run dev

web-check: ## Lint, type check and format check the frontend
	cd apps/web && npm run lint && npm run typecheck && npm run format:check

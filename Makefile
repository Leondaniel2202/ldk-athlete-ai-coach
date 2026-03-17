UV_CACHE_DIR ?= .uv-cache
UV = uv --cache-dir $(UV_CACHE_DIR)

.PHONY: help install update lock add remove api db-up db-down test lint lint-fix format-check type-check alembic-up alembic-revision

help: ## Show this help message
	@$(UV) run python -c "import re; [print('  {:<22} {}'.format(*m.groups())) for line in open('Makefile') for m in [re.match(r'^([a-zA-Z_-]+):.*##\s*(.*)', line)] if m]"

## ── Dependencies ──────────────────────────────────────────────────────────────

install: ## Install all dependencies (including dev)
	$(UV) sync --group dev

update: ## Upgrade all dependencies to latest allowed versions
	$(UV) sync --upgrade --group dev

lock: ## Refresh the lockfile without installing
	$(UV) lock

add: ## Add a runtime dependency, e.g. make add PKG=httpx
	$(UV) add $(PKG)

add-dev: ## Add a dev dependency, e.g. make add-dev PKG=pytest
	$(UV) add --dev $(PKG)

remove: ## Remove a dependency, e.g. make remove PKG=httpx
	$(UV) remove $(PKG)

## ── Application ───────────────────────────────────────────────────────────────

api: ## Start the FastAPI development server with auto-reload
	$(UV) run uvicorn ldk_athlete_ai_coach.main:app --reload

## ── Database ──────────────────────────────────────────────────────────────────

db-up: ## Start the PostgreSQL Docker container
	docker compose up -d postgres

db-down: ## Stop all Docker Compose services
	docker compose down

alembic-up: ## Apply all pending Alembic migrations
	$(UV) run alembic upgrade head

alembic-revision: ## Generate a new Alembic migration, e.g. make alembic-revision MSG="add table"
	$(UV) run alembic revision --autogenerate -m "$(MSG)"

## ── Quality ───────────────────────────────────────────────────────────────────

test: ## Run the test suite
	$(UV) run pytest

lint: ## Check code with ruff
	$(UV) run ruff check .

lint-fix: ## Auto-fix ruff lint violations
	$(UV) run ruff check . --fix

format-check: ## Check formatting with ruff (no writes)
	$(UV) run ruff format --check .

type-check: ## Run mypy static type checking
	$(UV) run mypy src tests

UV_CACHE_DIR ?= .uv-cache
UV = uv --cache-dir $(UV_CACHE_DIR)

.PHONY: help \
        install update lock add remove \
        api \
        db-up db-test-up db-down \
        test test-unit test-integration test-api test-cov \
        lint lint-fix format-check type-check \
        alembic-up alembic-revision \
        frontend-install frontend-dev frontend-build frontend-lint \
        frontend-format-check frontend-type-check

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

db-up: ## Start the development PostgreSQL container
	docker compose up -d postgres

db-test-up: ## Start the test PostgreSQL container (postgres_test on port 5433)
	docker compose up -d postgres_test

db-down: ## Stop all Docker Compose services
	docker compose down

alembic-up: ## Apply all pending Alembic migrations
	$(UV) run alembic upgrade head

alembic-revision: ## Generate a new Alembic migration, e.g. make alembic-revision MSG="add table"
	$(UV) run alembic revision --autogenerate -m "$(MSG)"

## ── Quality ───────────────────────────────────────────────────────────────────

test: ## Run the full test suite
	$(UV) run pytest

test-unit: ## Run only unit tests (COV=1 to enable coverage)
	$(UV) run pytest -m unit $(if $(COV),--cov=ldk_athlete_ai_coach --cov-report=term-missing)

test-integration: ## Run only integration tests (COV=1 to enable coverage)
	$(UV) run pytest -m integration $(if $(COV),--cov=ldk_athlete_ai_coach --cov-report=term-missing)

test-api: ## Run only API tests (COV=1 to enable coverage)
	$(UV) run pytest -m api $(if $(COV),--cov=ldk_athlete_ai_coach --cov-report=term-missing)

test-cov: ## Run tests with coverage output
	$(UV) run pytest --cov=ldk_athlete_ai_coach --cov-report=term-missing

lint: ## Check code with ruff
	$(UV) run ruff check .

lint-fix: ## Auto-fix ruff lint violations
	$(UV) run ruff check . --fix

format-check: ## Check formatting with ruff (no writes)
	$(UV) run ruff format --check .

format: ## Auto-fix formatting with ruff
	$(UV) run ruff format .

type-check: ## Run mypy static type checking
	$(UV) run mypy src tests

## ── Frontend ──────────────────────────────────────────────────────────────────

frontend-install: ## Install frontend dependencies
	cd frontend && npm install

frontend-dev: ## Start the Next.js development server (port 3000)
	cd frontend && npm run dev

frontend-build: ## Build the frontend for production
	cd frontend && npm run build

frontend-lint: ## Lint the frontend with ESLint
	cd frontend && npm run lint

frontend-format-check: ## Check frontend formatting with Prettier
	cd frontend && npm run format-check

frontend-type-check: ## Run TypeScript type checking for the frontend
	cd frontend && npm run type-check

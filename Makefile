UV_CACHE_DIR ?= .uv-cache

.PHONY: help \
        backend-install backend-update backend-lock backend-add backend-add-dev backend-remove \
        backend-api \
        backend-db-up backend-db-test-up backend-db-down \
        backend-test backend-test-unit backend-test-integration backend-test-api backend-test-cov \
        backend-lint backend-lint-fix backend-format-check backend-format backend-type-check \
        backend-alembic-up backend-alembic-revision \
        frontend-install frontend-dev frontend-build frontend-lint \
        frontend-format-check frontend-type-check \
        install test lint format-check type-check

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  %-30s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## -- Backend: Dependencies ---------------------------------------------------

backend-install: ## Install all backend dependencies (including dev)
	cd backend && uv --cache-dir ../.uv-cache sync --group dev

backend-update: ## Upgrade all backend dependencies to latest allowed versions
	cd backend && uv --cache-dir ../.uv-cache sync --upgrade --group dev

backend-lock: ## Refresh the backend lockfile without installing
	cd backend && uv --cache-dir ../.uv-cache lock

backend-add: ## Add a backend runtime dependency, e.g. make backend-add PKG=httpx
	cd backend && uv --cache-dir ../.uv-cache add $(PKG)

backend-add-dev: ## Add a backend dev dependency, e.g. make backend-add-dev PKG=pytest
	cd backend && uv --cache-dir ../.uv-cache add --dev $(PKG)

backend-remove: ## Remove a backend dependency, e.g. make backend-remove PKG=httpx
	cd backend && uv --cache-dir ../.uv-cache remove $(PKG)

## -- Backend: Application ----------------------------------------------------

backend-api: ## Start the FastAPI development server with auto-reload
	cd backend && uv --cache-dir ../.uv-cache run uvicorn ldk_athlete_ai_coach.main:app --reload

## -- Backend: Database -------------------------------------------------------

backend-db-up: ## Start the development PostgreSQL container
	cd backend && docker compose up -d postgres

backend-db-test-up: ## Start the test PostgreSQL container (postgres_test on port 5433)
	cd backend && docker compose up -d postgres_test

backend-db-down: ## Stop all backend Docker Compose services
	cd backend && docker compose down

backend-alembic-up: ## Apply all pending Alembic migrations
	cd backend && uv --cache-dir ../.uv-cache run alembic upgrade head

backend-alembic-revision: ## Generate a new Alembic migration, e.g. make backend-alembic-revision MSG="add table"
	cd backend && uv --cache-dir ../.uv-cache run alembic revision --autogenerate -m "$(MSG)"

## -- Backend: Quality --------------------------------------------------------

backend-test: ## Run the full backend test suite
	cd backend && uv --cache-dir ../.uv-cache run pytest

backend-test-unit: ## Run only backend unit tests (COV=1 to enable coverage)
	cd backend && uv --cache-dir ../.uv-cache run pytest -m unit $(if $(COV),--cov=ldk_athlete_ai_coach --cov-report=term-missing)

backend-test-integration: ## Run only backend integration tests (COV=1 to enable coverage)
	cd backend && uv --cache-dir ../.uv-cache run pytest -m integration $(if $(COV),--cov=ldk_athlete_ai_coach --cov-report=term-missing)

backend-test-api: ## Run only backend API tests (COV=1 to enable coverage)
	cd backend && uv --cache-dir ../.uv-cache run pytest -m api $(if $(COV),--cov=ldk_athlete_ai_coach --cov-report=term-missing)

backend-test-cov: ## Run backend tests with coverage output
	cd backend && uv --cache-dir ../.uv-cache run pytest --cov=ldk_athlete_ai_coach --cov-report=term-missing

backend-lint: ## Check backend code with ruff
	cd backend && uv --cache-dir ../.uv-cache run ruff check .

backend-lint-fix: ## Auto-fix backend ruff lint violations
	cd backend && uv --cache-dir ../.uv-cache run ruff check . --fix

backend-format-check: ## Check backend formatting with ruff (no writes)
	cd backend && uv --cache-dir ../.uv-cache run ruff format --check .

backend-format: ## Auto-fix backend formatting with ruff
	cd backend && uv --cache-dir ../.uv-cache run ruff format .

backend-type-check: ## Run mypy static type checking for the backend
	cd backend && uv --cache-dir ../.uv-cache run mypy src tests

## -- Frontend ----------------------------------------------------------------

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

## -- Aggregate aliases -------------------------------------------------------

install: backend-install ## Install backend dependencies (alias for backend-install; run frontend-install separately)

test: backend-test ## Run the full backend test suite (alias for backend-test)

lint: backend-lint ## Check backend code with ruff (alias for backend-lint)

format-check: backend-format-check ## Check backend formatting (alias for backend-format-check)

type-check: backend-type-check ## Run mypy for the backend (alias for backend-type-check)

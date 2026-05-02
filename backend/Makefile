AWK ?= awk
BACKEND_DIR ?= $(if $(wildcard pyproject.toml),.,backend)
BACKEND_MAKEFILE := $(lastword $(MAKEFILE_LIST))
UV_CACHE_DIR ?= .uv-cache

.PHONY: backend-help \
        backend-install backend-update backend-lock backend-add backend-add-dev backend-remove \
        backend-api \
        backend-db-up backend-db-test-up backend-db-down \
        backend-test backend-test-unit backend-test-integration backend-test-api backend-test-cov \
        backend-lint backend-lint-fix backend-format-check backend-format backend-type-check \
        backend-alembic-up backend-alembic-revision

ifneq ($(wildcard pyproject.toml),)
.DEFAULT_GOAL := help
.PHONY: help
help: backend-help
endif

backend-help:
	@powershell -NoProfile -Command "$$files = @('$(BACKEND_MAKEFILE)'); $$awk = Get-Command '$(AWK)' -ErrorAction SilentlyContinue; if ($$awk) { & $$awk.Source 'BEGIN { FS = "":.*##""; print ""Available backend commands:"" } /^backend-[a-zA-Z0-9_-]+:.*##/ { gsub(/^[ \t]+|[ \t]+$$/, """", $$2); printf ""  %-30s %s\n"", $$1, $$2 }' $$files } else { 'Available backend commands:'; foreach ($$file in $$files) { Get-Content $$file | Where-Object { $$_ -match '^backend-[a-zA-Z0-9_-]+:.*##' } | ForEach-Object { $$parts = $$_ -split ':.*##', 2; '  {0,-30} {1}' -f $$parts[0].Trim(), $$parts[1].Trim() } } }"

## -- Backend: Dependencies ---------------------------------------------------

backend-install: ## Install all backend dependencies (including dev)
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) sync --group dev

backend-update: ## Upgrade all backend dependencies to latest allowed versions
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) sync --upgrade --group dev

backend-lock: ## Refresh the backend lockfile without installing
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) lock

backend-add: ## Add a backend runtime dependency, e.g. make backend-add PKG=httpx
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) add $(PKG)

backend-add-dev: ## Add a backend dev dependency, e.g. make backend-add-dev PKG=pytest
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) add --dev $(PKG)

backend-remove: ## Remove a backend dependency, e.g. make backend-remove PKG=httpx
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) remove $(PKG)

## -- Backend: Application ----------------------------------------------------

backend-api: ## Start the FastAPI development server with auto-reload
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run uvicorn ldk_athlete_ai_coach.main:app --reload

## -- Backend: Database -------------------------------------------------------

backend-db-up: ## Start the development PostgreSQL container
	cd $(BACKEND_DIR) && docker compose up -d postgres

backend-db-test-up: ## Start the test PostgreSQL container (postgres_test on port 5433)
	cd $(BACKEND_DIR) && docker compose up -d postgres_test

backend-db-down: ## Stop all backend Docker Compose services
	cd $(BACKEND_DIR) && docker compose down

backend-alembic-up: ## Apply all pending Alembic migrations
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run alembic upgrade head

backend-alembic-revision: ## Generate a new Alembic migration, e.g. make backend-alembic-revision MSG="add table"
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run alembic revision --autogenerate -m "$(MSG)"

## -- Backend: Quality --------------------------------------------------------

backend-test: ## Run the full backend test suite
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run pytest

backend-test-unit: ## Run only backend unit tests (COV=1 to enable coverage)
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run pytest -m unit $(if $(COV),--cov=ldk_athlete_ai_coach --cov-report=term-missing)

backend-test-integration: ## Run only backend integration tests (COV=1 to enable coverage)
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run pytest -m integration $(if $(COV),--cov=ldk_athlete_ai_coach --cov-report=term-missing)

backend-test-api: ## Run only backend API tests (COV=1 to enable coverage)
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run pytest -m api $(if $(COV),--cov=ldk_athlete_ai_coach --cov-report=term-missing)

backend-test-cov: ## Run backend tests with coverage output
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run pytest --cov=ldk_athlete_ai_coach --cov-report=term-missing

backend-lint: ## Check backend code with ruff
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run ruff check .

backend-lint-fix: ## Auto-fix backend ruff lint violations
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run ruff check . --fix

backend-format-check: ## Check backend formatting with ruff (no writes)
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run ruff format --check .

backend-format: ## Auto-fix backend formatting with ruff
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run ruff format .

backend-type-check: ## Run mypy static type checking for the backend
	cd $(BACKEND_DIR) && uv --cache-dir $(UV_CACHE_DIR) run mypy src tests

UV_CACHE_DIR ?= .uv-cache
UV = uv --cache-dir $(UV_CACHE_DIR)

.PHONY: install api db-up db-down test lint format-check type-check alembic-up alembic-revision

install:
	$(UV) sync --group dev

api:
	$(UV) run uvicorn ldk_athlete_ai_coach.main:app --reload

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

test:
	$(UV) run pytest

lint:
	$(UV) run ruff check .

lint-fix:
	$(UV) run ruff check . --fix	

format-check:
	$(UV) run ruff format --check .

type-check:
	$(UV) run mypy src tests

alembic-up:
	$(UV) run alembic upgrade head

alembic-revision:
	$(UV) run alembic revision --autogenerate -m "$(MSG)"

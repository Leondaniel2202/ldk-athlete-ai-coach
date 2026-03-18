.PHONY: install lint lint-fix format-check type-check test api db-up db-down alembic-up alembic-revision

install:
	uv sync --all-groups

lint:
	uv run ruff check src/ tests/

lint-fix:
	uv run ruff check --fix src/ tests/

format-check:
	uv run ruff format --check src/ tests/

type-check:
	uv run mypy src/

test:
	uv run pytest tests/ -v

api:
	uv run python -m app.main

db-up:
	docker compose up -d db

db-down:
	docker compose down db

alembic-up:
	uv run alembic upgrade head

alembic-revision:
	uv run alembic revision --autogenerate -m "$(MSG)"

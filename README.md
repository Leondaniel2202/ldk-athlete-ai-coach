# ldk-athlete-ai-coach

Minimal backend foundation for the LDK Athlete AI Coach project.

## Stack

- Python 3.12
- uv
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- pytest
- ruff
- mypy

## Included in this foundation

- `src`-layout FastAPI application
- Centralized settings via `pydantic-settings`
- PostgreSQL via Docker Compose
- SQLAlchemy session/base setup
- Alembic migration scaffold
- Basic API and config tests
- Simple developer commands via `Makefile`

## Project structure

```text
src/
  ldk_athlete_ai_coach/
    api/
    core/
    db/
    main.py
tests/
alembic/
```

## Prerequisites

- Python 3.12
- `uv`
- Docker Desktop or a compatible Docker runtime

## Setup

1. Create the local environment file.

```powershell
Copy-Item .env.example .env
```

2. Install dependencies.

```powershell
make install
```

If `make` is not available, run:

```powershell
uv --cache-dir .uv-cache sync --group dev
```

## Run the database

```powershell
make db-up
```

To stop the containers:

```powershell
make db-down
```

## Run the API

```powershell
make api
```

The service exposes:`r`n`r`n- `GET /``r`n- `GET /api/v1/health``r`n- `POST /api/v1/notion/sync`

## Quality checks

Run the test suite:

```powershell
make test
```

Run linting:

```powershell
make lint
```

Run formatting checks:

```powershell
make format-check
```

Run type checking:

```powershell
make type-check
```

## Database migrations

Apply migrations:

```powershell
make alembic-up
```

Create a new migration:

```powershell
make alembic-revision MSG="describe_change"
```

## Troubleshooting

If you see an error similar to `No Python at ...` from `.venv` on Windows, the
virtual environment was likely created from an unavailable interpreter. Install
Python 3.12, recreate the virtual environment, and then rerun the `uv` install
command.


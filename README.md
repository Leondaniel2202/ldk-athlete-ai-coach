# ldk-athlete-ai-coach

Backend-first training management and analysis platform for a personal athlete workflow.

V1 was backend-only. V2 introduces a React/Next.js frontend and a monorepo structure
with separate `backend/` and `frontend/` areas.

V1 kept Notion as the operational source of truth, mirrored structured training data into
PostgreSQL, exposed read-oriented FastAPI endpoints, and added an initial AI analysis
layer on top of structured workout and phase context.

## V1 scope

- Sync plans, phases, workouts, events, tracked sessions, nutrition guidelines, and
  weekly feedback from Notion into PostgreSQL
- Expose resource endpoints for plans, phases, workouts, and sessions
- Build richer context snapshots for workouts, phase weeks, and full phases
- Calculate lifecycle status and basic training-load adherence metrics
- Provide structured AI analysis for workout and phase context

V1 does not replace Notion yet. Write flows still start in Notion, sync is one-way into
the backend, and AI is limited to analysis rather than generation or automation.

## Stack

**Backend**

- Python 3.12
- `uv`
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Notion API
- OpenAI Responses API
- pytest
- ruff
- mypy

**Frontend** (V2)

- Next.js 16
- React 19
- TypeScript
- Node.js 20+

## Repository Layout

```text
ldk-athlete-ai-coach/
  backend/
    pyproject.toml
    uv.lock
    alembic/
    src/
    tests/
    docker-compose.yml
    .env.example

  frontend/
    package.json
    next.config.ts
    tsconfig.json
    app/
    components/
    lib/
    hooks/
    types/
    public/
    .env.local.example

  docs/
  .github/
  AGENTS.md
  CHANGELOG.md
  README.md
  Makefile
  .gitignore
```

## Quick Start

### Backend

1. Copy the example environment file.

```powershell
Copy-Item backend/.env.example backend/.env
```

2. Install backend dependencies.

```powershell
make backend-install
```

3. Start the local development database.

```powershell
make backend-db-up
```

4. Apply migrations.

```powershell
make backend-alembic-up
```

5. Start the API.

```powershell
make backend-api
```

6. Verify the service.

```text
GET  /                  -> root status message
GET  /api/v1/system/health
GET  /docs              -> Swagger UI
```

### Frontend

1. Install frontend dependencies.

```powershell
make frontend-install
```

2. Copy the frontend environment file.

```powershell
Copy-Item frontend/.env.local.example frontend/.env.local
```

3. Start the frontend development server.

```powershell
make frontend-dev
```

The frontend runs at `http://localhost:3000`. Start the backend first to see a connected
state.

## Common Commands

```powershell
make help
make backend-test
make backend-test-unit
make backend-test-integration
make backend-test-api
make backend-test-cov
make backend-lint
make backend-format-check
make backend-type-check
make backend-db-test-up
make backend-db-down
make frontend-lint
make frontend-format-check
make frontend-type-check
make frontend-build
```

## Documentation

- [Documentation Home](docs/index.md)
- [Local Development Guide](docs/getting-started/local-dev.md)
- [System Map](docs/architecture/system-map.md)
- [Domain Model](docs/domain/model.md)
- [Notion Integration](docs/integrations/notion.md)
- [API Overview](docs/api/overview.md)
- [AI Overview](docs/ai/overview.md)
- [Operations Runbook](docs/operations/runbook.md)
- [Testing Guide](docs/testing.md)
- [V1 Release Summary](docs/releases/v1.md)
- [Current Architecture](docs/architecture/current-architecture.md)
- [Product Vision](docs/vision/system-overview.md)
- [Roadmap](docs/roadmap/roadmap.md)

## Current API Surface

The current API is organized into five route groups under `/api/v1`:

- `resources`: raw entity access for plans, phases, workouts, and sessions
- `context`: aggregated workout, phase-week, and phase snapshots
- `ai`: structured analysis of workout and phase context
- `sync`: blocking one-way Notion sync
- `system`: health checks

The `/api/v1` path version is the transport/API version. It is not the same thing as
the product/repository "V1" milestone documented in [docs/releases/v1.md](docs/releases/v1.md).

## Current Limitations

- Notion remains the source of truth for planning and most write operations
- External training data still reaches the backend indirectly through Notion
- The API is primarily read-oriented in V1
- AI is analysis-only in V1 and depends on `OPENAI_API_KEY`
- The system is designed for single-user personal use at this stage

## Troubleshooting

- If `.venv` points to an unavailable Python interpreter on Windows, recreate the
  environment with Python 3.12 and rerun `make backend-install`.
- If the API starts but resource endpoints fail, verify that Postgres is running and
  migrations have been applied.
- If sync or AI endpoints fail, check the relevant environment variables in
  `backend/.env`.

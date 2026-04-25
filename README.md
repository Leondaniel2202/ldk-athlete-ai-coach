# ldk-athlete-ai-coach

Backend-first training management and analysis platform for a personal athlete workflow.

V1 keeps Notion as the operational source of truth, mirrors the structured training
data into PostgreSQL, exposes read-oriented FastAPI endpoints, and adds an initial AI
analysis layer on top of structured workout and phase context.

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

## Quick Start

1. Copy the example environment file.

```powershell
Copy-Item .env.example .env
```

2. Install runtime and development dependencies.

```powershell
make install
```

3. Start the local development database.

```powershell
make db-up
```

4. Apply migrations.

```powershell
make alembic-up
```

5. Start the API.

```powershell
make api
```

6. Verify the service.

```text
GET  /                  -> root status message
GET  /api/v1/system/health
GET  /docs              -> Swagger UI
```

## Common Commands

```powershell
make help
make test
make test-unit
make test-integration
make test-api
make test-cov
make lint
make format-check
make type-check
make db-test-up
make db-down
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

## Repository Layout

```text
src/ldk_athlete_ai_coach/
  ai/                  LLM client, prompts, AI services, AI schemas
  api/                 FastAPI routers and transport schemas
  application/         Context-building application services
  core/                Settings, logging, Notion integration
  db/                  SQLAlchemy models, repositories, session management
  domain/              Status and metrics logic
  utils/               Shared date helpers
  main.py              FastAPI entrypoint
tests/                 Unit, integration, and API tests
alembic/               Database migration environment and revisions
docs/                  Narrative and operational documentation
```

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
  environment with Python 3.12 and rerun `make install`.
- If the API starts but resource endpoints fail, verify that Postgres is running and
  migrations have been applied.
- If sync or AI endpoints fail, check the relevant environment variables in `.env`.


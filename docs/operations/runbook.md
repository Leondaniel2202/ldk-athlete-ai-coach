# Operations Runbook

This runbook covers the recurring operational tasks needed to run and troubleshoot the
v1 backend in local and development-style environments.

## Daily Startup

1. Ensure `.env` is populated.
2. Start the development database.
3. Apply migrations.
4. Start the API.
5. Verify health.
6. Run Notion sync if the database needs fresh data.

Commands:

```powershell
make db-up
make alembic-up
make api
```

Smoke checks:

- `GET /`
- `GET /api/v1/system/health`
- `GET /docs`

## Shutdown

Stop compose services:

```powershell
make db-down
```

## Database Operations

### Start development database

```powershell
make db-up
```

### Start test database

```powershell
make db-test-up
```

### Apply migrations

```powershell
make alembic-up
```

### Create migration

```powershell
make alembic-revision MSG="describe_change"
```

## Notion Sync Operations

### Normal sync

Call:

```text
POST /api/v1/sync/notion
```

This runs the full sync and returns a per-entity summary.

### Debug sync

Call:

```text
POST /api/v1/sync/notion?hard_fail=true
```

Use this when you want the sync to stop at the first extraction or persistence failure.

### What to watch

- entity-level fetched/success/failed counts
- `502` means upstream Notion authentication/access/downstream failure
- `503` means rate-limit retries were exhausted
- `500` with a summary body means the sync finished but some entity batches failed
- `500` with structured detail means hard-fail mode aborted early

## AI Operations

AI routes:

- `POST /api/v1/ai/analysis/specific-phase-context/{phase_id}`
- `POST /api/v1/ai/analysis/specific-workout-context/{workout_id}`

Prerequisites:

- synced database content
- valid `OPENAI_API_KEY`

Common failure modes:

- missing key or invalid configuration
- provider request failure
- invalid structured output from provider

Current API behavior:

- AI failures surface as `503`

## Health and Observability

### Health endpoint

```text
GET /api/v1/system/health
```

Expected payload:

```json
{
  "status": "ok"
}
```

### Root endpoint

```text
GET /
```

Expected payload:

```json
{
  "message": "ldk-athlete-ai-coach backend"
}
```

### Logging

Logging is configured in `core/logging.py`.

- `DEBUG=true` enables debug-level logging
- otherwise the app runs at info level

The Notion integration logs major sync operations, retries, and failures. FastAPI and
HTTP client activity will also become more visible in debug mode.

## Common Incidents

## API starts but returns database errors

Checks:

- is `postgres` running?
- does `.env` point to the correct database host and port?
- have migrations been applied?

## Sync returns `502`

Checks:

- `NOTION_API_KEY` valid?
- data source IDs correct?
- integration still has access to the target resources?

## Sync returns `503`

Checks:

- repeated rate limiting from Notion
- temporary upstream throttling

Recommended action:

- retry later
- reduce repeated manual sync attempts during debugging

## Sync returns `500`

Two likely cases:

- hard-fail mode aborted on the first bad row or persistence error
- non-strict mode completed but one or more entity batches failed

Recommended action:

- rerun with `hard_fail=true`
- inspect which entity type failed
- check extraction assumptions and dependency resolution

## AI routes return `503`

Checks:

- is `OPENAI_API_KEY` present?
- is the key valid?
- is the provider reachable?
- is the context valid enough to produce a schema-conforming result?

## Tests fail against missing database

Checks:

- run `make db-test-up`
- ensure test DB env values match the compose service

## Routine Maintenance

- keep migrations current with model changes
- rerun sync after Notion schema changes
- keep `.env.example` aligned with settings
- run lint, format, type-check, and tests before merging significant backend changes

## Safe Change Order

When changing the persistence or integration layer, the safest order is:

1. update ORM model or schema expectations
2. add or update migration
3. update extractor or mapper behavior
4. update persistence logic if needed
5. update tests
6. run a sync in a disposable environment

That order reduces the chance of introducing mismatched sync and persistence behavior.

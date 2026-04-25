# Testing Guide

The repository uses pytest with a layered test strategy that matches the architecture of
the backend.

Backend tests live under `backend/tests/`. Backend tooling is configured in
`backend/pyproject.toml`. All backend make targets use the `backend-` prefix.

## Goals

The current test suite is designed to give confidence in:

- settings and infrastructure wiring
- domain calculation rules
- repository query behavior
- Notion extraction, mapping, sync, and persistence logic
- application-level context construction
- API route behavior
- AI prompt and service behavior without relying on live provider calls

## Tooling

Configured in `backend/pyproject.toml`:

- `pytest`
- `pytest-cov`
- markers: `unit`, `integration`, `api`

Coverage is configured for `src/ldk_athlete_ai_coach`.

## Test Layers

## Unit Tests

Purpose:

- validate pure logic and narrow components without external services

Current areas:

- config
- db import safety
- date utilities
- domain status and training-metrics calculators
- application context services
- AI prompt and analysis services
- OpenAI client behavior
- Notion client, extractors, mappers, and sync service logic

Run:

```powershell
make backend-test-unit
```

## Integration Tests

Purpose:

- validate real interactions against the dedicated test database

Current areas:

- model metadata
- repositories
- phase-context service integration
- Notion persistence behavior

Run:

```powershell
make backend-db-test-up
make backend-test-integration
```

## API Tests

Purpose:

- validate FastAPI routes and response contracts using `TestClient`

Current areas:

- health endpoint
- resource endpoints
- context endpoints
- Notion sync API
- AI analysis API

Run:

```powershell
make backend-db-test-up
make backend-test-api
```

## Full Suite

Run everything:

```powershell
make backend-test
```

Run everything with coverage:

```powershell
make backend-test-cov
```

## Test Support Code

The suite includes shared support code in `backend/tests/factories/` for:

- database helpers
- in-memory training models
- persisted training models
- Notion schema fixtures
- settings fixtures

This is a strong part of the test design because it keeps setup noise out of the actual
assertions.

## Current Layout

The preferred structure is the layered one:

- `backend/tests/unit/`
- `backend/tests/integration/`
- `backend/tests/api/`
- `backend/tests/factories/`

There are also older flat tests at the root of `backend/tests/` covering similar areas.
They represent earlier iterations of the suite. Going forward, new tests should follow
the layered structure and the older flat tests should be consolidated over time rather
than expanded further.

## What The Suite Covers Well

- status calculation rules
- repository query semantics
- Notion extraction edge cases
- sync orchestration behavior
- context response construction
- structured AI request/response flow
- route-level HTTP behavior for the main API groups

## What The Suite Does Not Fully Guarantee

- production-scale performance
- long-running sync behavior against live Notion data
- end-to-end AI quality against real provider variability
- full operational behavior in deployed environments

That is normal for v1. The current suite is strong on correctness and contract behavior,
not on production ops simulation.

## Recommended Workflow

During day-to-day development:

1. run focused unit tests while changing logic
2. run integration or API tests when touching repositories, persistence, or routes
3. run `make backend-test-cov` before finishing larger backend work

Before merging:

- `make backend-lint`
- `make backend-format-check`
- `make backend-type-check`
- relevant test targets, or the full suite for broader changes

## When To Add Which Test

- add a unit test when the behavior is mostly pure logic or a narrow class contract
- add an integration test when a repository or persistence boundary changes
- add an API test when a route, schema, or HTTP-level error mapping changes

This keeps the suite aligned with the layered architecture instead of turning every test
into an expensive end-to-end case.

# Repository Instructions For Coding Agents

This file is the shared repository guidance for coding agents that support repo-level
instruction files.

It complements, but does not replace, agent-specific integrations such as
`.github/copilot-instructions.md`.

## What this repository is

`ldk-athlete-ai-coach` is a backend-first training platform.

Current state:

- Notion remains the operational source of truth
- the backend mirrors structured training data into PostgreSQL
- FastAPI exposes resource, context, AI, sync, and system routes
- application services build richer workout and phase context
- domain logic calculates status and basic adherence metrics
- the AI layer performs structured analysis on backend-owned context models

## Version naming

Keep these separate:

- product milestone `V1`: `docs/releases/v1.md`
- HTTP API version: `/api/v1`
- living architecture docs:
  - `docs/architecture/current-architecture.md`
  - `docs/architecture/system-map.md`

Do not use `v1` ambiguously in code or docs.

## Default working rules

- Keep scope tight.
- Prefer the existing architecture and patterns.
- Do not refactor unrelated code.
- Do not add broad abstractions without a clear reason.
- Do not redesign the system unless explicitly asked.
- When unclear, make the smallest safe change that satisfies the request.

## Architecture boundaries

Respect these roles:

- `api`: request parsing, dependency wiring, response models, HTTP error mapping
- `application`: orchestration and context assembly
- `domain`: status rules, metrics, shared domain concepts
- `db`: persistence models, repositories, sessions
- `core`: settings, logging, Notion integration infrastructure
- `ai`: prompt builders, provider calls, structured result validation

Non-negotiables:

- no direct database logic in API routes
- no prompt-building in API routes
- no transport concerns inside domain logic
- no raw external payloads flowing into domain logic when a mapping layer exists
- no provider-specific assumptions spread across the codebase

## Repository-specific rules

### Notion sync

- Preserve the current one-way sync model unless explicitly asked to change it.
- Keep the fetch/extract/map/persist split intact.
- Match rows by `notion_page_id`.
- Keep foreign-key resolution in the persistence layer.
- Update `docs/integrations/notion.md` if sync behavior changes.

### Database and config

- Keep ORM changes in `db/models`.
- Keep query logic in repositories.
- Add or update Alembic migrations for schema changes when appropriate.
- Keep `.env.example` aligned with `core/config.py`.
- Update `docs/domain/model.md` if model meaning changes.

### API

- Keep routes thin and explicit.
- Use Pydantic schemas for contracts.
- Preserve current route grouping unless the task explicitly changes API structure.
- Update `docs/api/overview.md` when contracts or route responsibilities change.

### AI

- Build AI on structured backend context, not raw Notion payloads.
- Prefer explicit prompt builders and schema-validated outputs.
- Keep model/provider interaction behind the integration layer.
- Update `docs/ai/overview.md` when AI behavior or surface area changes.

### Docs

- Update living docs in place, issue by issue, in the same change that updates the
  behavior when practical.
- Use `docs/releases/` for milestone snapshots, not living architecture state.
- Update the relevant docs when these areas change:
  - `docs/architecture/current-architecture.md` and
    `docs/architecture/system-map.md` when structure, boundaries, or main flow change
  - `docs/api/overview.md` when routes, contracts, or API responsibilities change
  - `docs/domain/model.md` when entities, meanings, or domain rules change
  - `docs/integrations/notion.md` when sync behavior or Notion assumptions change
  - `docs/operations/runbook.md` and `docs/getting-started/local-dev.md` when setup,
    commands, or operational steps change
  - `docs/testing.md` when the testing structure, strategy, or confidence boundaries
    change
  - `docs/releases/v1.md` stays mostly stable as the v1 milestone snapshot
  - when v2 is done, create `docs/releases/v2.md` and do a full docs review pass
- Keep comments minimal and factual.
- If you change behavior, update the nearest relevant docs.

## Development workflow

Use the `Makefile` as the canonical workflow entry point.

Preferred commands:

```bash
make help
make install
make api
make db-up
make db-test-up
make db-down
make alembic-up
make alembic-revision MSG="description"
make lint
make lint-fix
make format-check
make type-check
make test
make test-unit
make test-integration
make test-api
make test-cov
```

Dependencies are managed with `uv`.

## Validation

Run the relevant existing checks before finishing.

At minimum, use these when relevant:

```bash
make lint
make type-check
make test
```

If formatting matters:

```bash
make format-check
```

If tests exist for the affected area:

- update them when behavior changes
- do not ignore failures
- do not delete them unless explicitly requested

## Avoid unless explicitly requested

- large refactors
- broad renames
- new frameworks
- write-back sync to Notion
- CI/CD changes
- infra or deployment changes
- unrelated code or docs cleanup

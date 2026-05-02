# Repository Instructions For Coding Agents

This file is the shared repository guidance for coding agents that support repo-level
instruction files.

It complements, but does not replace, agent-specific integrations such as
`.github/copilot-instructions.md`.

## What this repository is

`ldk-athlete-ai-coach` is a backend-first training platform moving into V2 with a
monorepo structure.

Current state:

- Notion remains the operational source of truth
- the backend mirrors structured training data into PostgreSQL
- FastAPI exposes resource, context, AI, sync, and system routes
- application services build richer workout and phase context
- domain logic calculates status and basic adherence metrics
- the AI layer performs structured analysis on backend-owned context models
- a React/Next.js frontend scaffold is in place under `frontend/` (V2)

## Repository structure

```text
ldk-athlete-ai-coach/
  backend/       Python/FastAPI backend (Makefile, pyproject.toml, src/, tests/, alembic/, etc.)
  frontend/      Next.js/React/TypeScript frontend (Makefile, package.json, app/, etc.)
  docs/          Shared documentation
  .github/       GitHub Actions workflows and Copilot instructions
  AGENTS.md      This file
  CHANGELOG.md
  README.md
  Makefile       Root Makefile — canonical developer entry point for both backend and frontend
  .gitignore
```

Backend files (`Makefile`, `pyproject.toml`, `uv.lock`, `src/`, `tests/`, `alembic/`,
`docker-compose.yml`, `.env.example`) live in `backend/`. Frontend files
(`Makefile`, `package.json`, `app/`, etc.) live in `frontend/`. Root contains
repo/product-level files and the delegating `Makefile`.

## Branch policy (V2)

- `main` is the stable release branch
- `v2` is the active V2 integration branch
- V2 issue branches should branch from `v2`
- V2 PRs should target `v2`
- backend changes should stay in `backend/`
- frontend changes should stay in `frontend/`
- frontend and backend changes should not be mixed in one PR unless the issue explicitly
  requires it

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
- Application code should not be changed as part of structural/workflow tasks.

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
- Keep `backend/.env.example` aligned with `core/config.py`.
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

Use the root `Makefile` as the canonical workflow entry point for both backend and
frontend. It includes `backend/Makefile` and `frontend/Makefile`, so commands can also
be run from the matching subdirectory when useful.

### Backend commands (use `backend-` prefix)

```bash
make backend-install
make backend-api
make backend-db-up
make backend-db-test-up
make backend-db-down
make backend-alembic-up
make backend-alembic-revision MSG="description"
make backend-lint
make backend-lint-fix
make backend-format-check
make backend-type-check
make backend-test
make backend-test-unit
make backend-test-integration
make backend-test-api
make backend-test-cov
```

### Frontend commands (use `frontend-` prefix)

```bash
make frontend-install
make frontend-dev
make frontend-build
make frontend-lint
make frontend-format-check
make frontend-type-check
```

### Aggregate aliases

- `make install` — alias for `make backend-install`
- `make test` — alias for `make backend-test`
- `make lint` — alias for `make backend-lint`
- `make format-check` — alias for `make backend-format-check`
- `make type-check` — alias for `make backend-type-check`

Backend dependencies are managed with `uv` from within `backend/`.

## Validation

Run the relevant existing checks before finishing.

At minimum, use these when relevant:

```bash
make backend-lint
make backend-type-check
make backend-test
```

If formatting matters:

```bash
make backend-format-check
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

## Changelog Policy

Content to add:

- This repository uses `CHANGELOG.md` as a milestone-based changelog.
- V1 is the first baseline release.
- During V2, meaningful PRs into `v2` should update the `[Unreleased]` section.
- Do not add changelog entries for every tiny internal change.
- Add a changelog entry when the PR includes:
  - new API endpoints
  - new frontend functionality
  - data model or migration changes
  - AI behavior changes
  - Notion sync behavior changes
  - important bug fixes
  - operational, CI, deployment, or developer workflow changes
  - architecture-significant refactors
- No changelog entry is needed for:
  - typo fixes
  - formatting-only changes
  - small internal refactors with no behavior change
  - test-only cleanup with no user/developer-facing impact
  - routine dependency bumps unless security-relevant or behavior-changing
- Changelog entries should be concise and written under the correct heading:
  - Added
  - Changed
  - Fixed
  - Removed
  - Known Limitations, only for release sections, not every PR
- If a PR is meaningful but does not update `CHANGELOG.md`, mention this in the PR description and explain why.
- For PRs into `v2`, prefer updating `[Unreleased]`.
- For PRs from `v2` into `main`, finalize the release section only when explicitly requested.

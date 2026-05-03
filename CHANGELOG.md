# Changelog

All notable changes to this project are documented here.

This project currently uses milestone-based versioning. During early development, changelog entries focus on meaningful system, architecture, API, data model, AI, and workflow changes rather than every individual commit.

## [Unreleased]

### Added

- Added `frontend/` directory with a Next.js 16 + React 19 + TypeScript application scaffold.
- Added App Router structure, reusable component directory, API integration layer, hooks, types, and feature directories.
- Added `lib/api/client.ts` base API client configurable via `NEXT_PUBLIC_API_BASE_URL`.
- Added `hooks/useBackendStatus` hook and `components/ui/StatusBadge` component for backend connectivity display.
- Added landing page placeholder with live backend status indicator.
- Added initial frontend app shell with Dashboard, Planner, Analyzer, and Coach routes.
- Added a mock-data-backed dashboard with current training overview, current plan, current phase, and weekly outlook sections.
- Added `frontend/.env.local.example` for environment variable documentation.
- Added ESLint and Prettier configuration for frontend linting and formatting.
- Added `frontend-install`, `frontend-dev`, `frontend-build`, `frontend-lint`, `frontend-format-check`, and `frontend-type-check` Makefile targets.
- Added minimal frontend unit, integration, and E2E test structure with Vitest, React Testing Library, coverage, and Playwright wiring.
- Documented frontend local development setup in `docs/getting-started/local-dev.md`.

### Changed

- Reorganized repository into a backend/frontend monorepo structure. Python/FastAPI backend moved from the repository root into `backend/`. Frontend scaffold remains under `frontend/`. Root now contains only repo/product-level files and the shared `Makefile`.
- Split Makefile command definitions into `backend/Makefile` and `frontend/Makefile`, with the root `Makefile` including both sub-Makefiles, delegating `backend` and `frontend` targets, and providing central/subdirectory help output.
- Backend `Makefile` commands renamed with `backend-` prefix (`backend-install`, `backend-api`, `backend-test`, `backend-lint`, `backend-format-check`, `backend-type-check`, `backend-db-up`, `backend-db-test-up`, `backend-db-down`, `backend-alembic-up`, `backend-alembic-revision`). Aggregate aliases (`install`, `test`, `lint`, `format-check`, `type-check`) delegate to their backend counterparts.
- CI workflows split into backend and frontend workflows. Backend CI uses `backend-` prefixed make commands and the `backend/uv.lock` cache key; frontend CI runs quality, unit, integration, and E2E checks.
- `AGENTS.md` updated to document the V2 monorepo structure, branch policy, and new command names.
- `docs/getting-started/local-dev.md`, `docs/testing.md`, and `docs/operations/runbook.md` updated to reflect the new directory layout and command names.

---

## [1.0.0] - 2026-04-25

### Added

- Established the backend-first V1 foundation for the Athlete AI Coach system.
- Added PostgreSQL-backed persistence for structured training data.
- Added Notion sync as the initial ingestion path into the backend.
- Added core domain entities for plans, phases, workouts, tracked sessions, events, feedback, and nutrition guidelines.
- Added repository-based data access.
- Added FastAPI resource endpoints for core training entities.
- Added structured context services for workout, phase-week, and phase context.
- Added initial domain logic for lifecycle status and training-load adherence calculations.
- Added initial AI analysis layer for workout and phase context.
- Added unit, integration, and API test structure.
- Added V1 project documentation and operational guides.

### Changed

- Shifted the project from an initial backend skeleton into a usable backend foundation that mirrors and analyzes the Notion-based training workflow.

### Known Limitations

- Notion remains the operational source of truth.
- Sync is one-way from Notion into the backend.
- API functionality is primarily read-oriented.
- AI functionality is limited to analysis.
- External training data still reaches the backend indirectly through Notion.
- The system is still single-user and personal-use focused.

# Changelog

All notable changes to this project are documented here.

This project currently uses milestone-based versioning. During early development, changelog entries focus on meaningful system, architecture, API, data model, AI, and workflow changes rather than every individual commit.

## [Unreleased]

_Issue [#73](../../issues/73) — Initial frontend app shell and dashboard (parent: issue [#48](../../issues/73) - V2.1)_

### Added

**Frontend**
- Added `frontend/` directory with a Next.js 15 + React 19 + TypeScript application scaffold using the App Router.
- Added reusable component directory, API integration layer, hooks, types, and feature directories.
- Added `lib/api/client.ts` base API client configurable via `NEXT_PUBLIC_API_BASE_URL`.
- Added `hooks/useBackendStatus` hook and `components/ui/StatusBadge` component for backend connectivity display.
- Added landing page placeholder with live backend status indicator.
- Added initial frontend app shell with Dashboard, Planner, Analyzer, and Coach routes.
- Added live-data-backed dashboard displaying current training overview, current plan, current phase, and weekly outlook sections; connected to the backend `GET /api/v1/dashboard/overview` endpoint.
- Added `frontend/.env.local.example` for environment variable documentation.
- Added ESLint and Prettier configuration for frontend linting and formatting.
- Added `frontend-install`, `frontend-dev`, `frontend-build`, `frontend-lint`, `frontend-format-check`, and `frontend-type-check` Makefile targets.
- Added frontend unit tests for UI components (`StatusBadge`, `PhaseCard`, `PlanCard`, `TrainingOverview`, `WeeklyOutlook`) and the `useBackendStatus` hook using Vitest and React Testing Library.
- Added frontend integration tests for `AppShell` and `DashboardPage`.
- Added Playwright E2E test configuration and initial test structure.
- Added Vitest coverage reporting configuration.

**Backend**
- Added `GET /api/v1/dashboard/overview` endpoint returning a structured training snapshot for the current week.
- Added `DashboardService` aggregating the active plan, active phase, current-week workouts, training-load metrics, and category/execution summary overview items.
- Added `DashboardDataResponse`, `OverviewItemResponse`, `PlanSummaryResponse`, and `WorkoutSummaryResponse` API schemas.
- Added `GET /api/v1/context/phases/{phase_id}/weeks` endpoint for phase-week context by phase ID and week start date.
- Added `list_within_effective_date_window` method to the workout repository.

### Changed

- Reorganized repository into a backend/frontend monorepo structure. Python/FastAPI backend moved from the repository root into `backend/`. Frontend scaffold lives under `frontend/`. Root contains only repo/product-level files and the shared `Makefile`.
- Refactored the Event persistence model for issue [#76](../../issues/76) to use lean backend domain fields for classification, scheduling, location, and status while preserving Notion identity fields.
- Refactored the Plan persistence model for issue [#76](../../issues/76) to use application-owned `description`, `start_date`, and `end_date` fields instead of Notion-shaped date/text fields.
- Refactored the Phase persistence model for issue [#76](../../issues/76) to use application-owned `description`, typed focus tags, `start_date`, and `end_date` fields while keeping Notion extraction as the source mapping boundary.
- Split Makefile command definitions into `backend/Makefile` and `frontend/Makefile`, with the root `Makefile` including both sub-Makefiles and providing central/subdirectory help output.
- Backend `Makefile` commands renamed with `backend-` prefix (`backend-install`, `backend-api`, `backend-test`, `backend-lint`, `backend-format-check`, `backend-type-check`, `backend-db-up`, `backend-db-test-up`, `backend-db-down`, `backend-alembic-up`, `backend-alembic-revision`). Aggregate aliases (`install`, `test`, `lint`, `format-check`, `type-check`) delegate to their backend counterparts.
- Phase context endpoint for week context changed from `GET /context/phases/week` to `GET /context/phases/{phase_id}/weeks` to be resource-oriented and support explicit phase scoping.
- Dashboard frontend components refactored to consume live backend data via the new `getDashboardOverview` API function; mock data layer removed.
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

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
- Added `frontend/.env.local.example` for environment variable documentation.
- Added ESLint and Prettier configuration for frontend linting and formatting.
- Added `frontend-install`, `frontend-dev`, `frontend-build`, `frontend-lint`, `frontend-format-check`, and `frontend-type-check` Makefile targets.
- Documented frontend local development setup in `docs/getting-started/local-dev.md`.

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
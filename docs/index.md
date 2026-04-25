# Documentation Home

This documentation set is the practical v1 handoff layer for the repository.

The existing architecture, vision, and roadmap documents explain why the system exists
and where it is going. The files added here focus on how the current v1 actually works,
how to run it, how the major subsystems fit together, and what a new engineer needs in
order to operate and extend it safely.

## Read First

- [Local Development Guide](getting-started/local-dev.md)
- [System Map](architecture/system-map.md)
- [Domain Model](domain/model.md)

## Subsystems

- [Notion Integration](integrations/notion.md)
- [API Overview](api/overview.md)
- [AI Overview](ai/overview.md)
- [Operations Runbook](operations/runbook.md)
- [Testing Guide](testing.md)

## Background and Strategy

- [Current Architecture](architecture/current-architecture.md)
- [Product Vision](vision/system-overview.md)
- [Roadmap](roadmap/roadmap.md)
- [V1 Release Summary](releases/v1.md)

## Naming Conventions

These three versioning concepts are separate and should stay separate:

- `docs/releases/v1.md` means the product/repository v1 milestone
- `/api/v1/...` means the current HTTP API version
- `docs/architecture/current-architecture.md` and `docs/architecture/system-map.md`
  are living architecture docs and should be updated in place rather than copied per
  product version unless you intentionally want a historical architecture snapshot

## What V1 Is

V1 is a backend-first system that:

- mirrors training data from Notion into PostgreSQL
- exposes structured read APIs for resources and aggregated training context
- calculates status and basic adherence metrics in the backend
- adds initial AI analysis on top of structured context

V1 is not yet the final product layer. Notion still owns the day-to-day workflow and
the backend is still maturing toward full ownership of write flows, richer validation,
direct external ingestion, and a custom frontend.

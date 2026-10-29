# Notion removal (V2)

The Notion runtime integration, `/api/v1/sync` route, client, extractors, mappers and sync-focused tests were removed on the `refactor/remove-notion` branch. PostgreSQL is now the operational source of truth. The backend no longer requires Notion credentials.

## Data preservation and unfinished migration

Existing database tables still include `notion_page_id`, `notion_url` and `notion_page_content` as legacy columns (some non-nullable), and some current API contracts/tests expose them. **These columns were deliberately not dropped**: removing them safely requires a backup, review of persisted data, changes to the ORM and test factories, and a carefully verified Alembic migration. No production database was connected or changed as part of this change.

Before adding standalone write endpoints, finish the data-model carve-out: decide how to preserve legacy workout content, eliminate requirements for Notion identifiers on new rows, create an Alembic migration, update factories/API schemas and run tests against a dedicated database. Historical migrations should remain in place for migration continuity.

The uv lockfile should be regenerated (`cd backend && uv lock`) following the manifest dependency removal; then run `make lint`, `make type-check`, `make test` and frontend checks. These checks have not been executed in this GitHub-only change.

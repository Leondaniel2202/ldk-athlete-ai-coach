# Notion Integration

Notion is the primary operational system in v1. Planning, tracking, and qualitative
feedback still originate there, and the backend mirrors that data into PostgreSQL for
structured access, analysis, and future ownership.

This document explains how the integration works today.

## Responsibilities

The Notion integration layer is responsible for:

- authenticating against the Notion API
- retrieving raw data source entries
- flattening page content into plain text when available
- extracting raw Notion payloads into validated Pydantic schemas
- mapping extracted schemas into ORM entities
- resolving foreign keys by Notion page ID
- persisting each entity type in dependency order

It is not responsible for:

- planning writes back into Notion
- bidirectional sync
- frontend-facing API contracts
- AI analysis

## Configuration

Required settings:

- `NOTION_API_KEY`
- `NOTION_PLAN_DATA_SOURCE_ID`
- `NOTION_PHASE_DATA_SOURCE_ID`
- `NOTION_NUTRITION_GUIDELINE_DATA_SOURCE_ID`
- `NOTION_WORKOUT_DATA_SOURCE_ID`
- `NOTION_EVENT_DATA_SOURCE_ID`
- `NOTION_SESSION_DATA_SOURCE_ID`
- `NOTION_FEEDBACK_DATA_SOURCE_ID`

Optional settings:

- `NOTION_PAGE_SIZE` default `100`
- `NOTION_TIMEOUT_SECONDS` default `30`
- `NOTION_MAX_RETRIES` default `3`

Backward compatibility:

The settings layer still accepts older `*_DB_ID` environment variables through
`AliasChoices` so older local setups continue to work while the codebase migrates to the
newer Notion data source API.

## Low-Level Client

The low-level client lives in `core/integrations/notion/client.py`.

Main responsibilities:

- initialize the official `notion-client` SDK with the configured token
- query Notion data sources
- iterate through paginated results
- retrieve database and data source metadata
- walk block children and flatten page content into plain text
- translate Notion SDK errors into domain-specific exceptions

Current behavior worth knowing:

- the configured Notion API version is `2026-03-11`
- `429` rate-limit responses are retried with a fixed `1.0s` wait
- the total attempts are `notion_max_retries + 1`
- `401` becomes `NotionAuthError`
- `403` and `404` become `NotionDatabaseNotFoundError`
- exhausted rate limits become `NotionRateLimitError`

## Sync Scope

The sync service currently supports seven Notion-backed entity groups.

| Sync key | Persisted entity | Env setting | Depends on |
| --- | --- | --- | --- |
| `plan` | `Plan` | `NOTION_PLAN_DATA_SOURCE_ID` | none |
| `nutrition_guideline` | `NutritionGuideline` | `NOTION_NUTRITION_GUIDELINE_DATA_SOURCE_ID` | none |
| `phase` | `Phase` | `NOTION_PHASE_DATA_SOURCE_ID` | plan, nutrition guideline |
| `workout` | `Workout` | `NOTION_WORKOUT_DATA_SOURCE_ID` | phase |
| `event` | `Event` | `NOTION_EVENT_DATA_SOURCE_ID` | plan, optional workout |
| `session` | `TrackedSession` | `NOTION_SESSION_DATA_SOURCE_ID` | optional workout |
| `feedback` | `WeeklyFeedback` | `NOTION_FEEDBACK_DATA_SOURCE_ID` | phase |

## Sync Order

`NotionSyncService.sync_all()` runs the full sync in this order:

1. plans
2. nutrition guidelines
3. phases
4. workouts
5. events
6. tracked sessions
7. weekly feedback

This order matches the dependency resolution in `NotionPersistenceService`.

## Sync Pipeline

The full flow for one entity type is:

1. fetch raw Notion pages via `NotionClient.iter_data_source_entries()`
2. extract each page into a validated schema via the relevant extractor
3. fetch and attach plain-text page content via `get_page_plain_text()`
4. open a DB session for the entity batch
5. map schemas into ORM entities through `NotionPersistenceService`
6. commit the transaction for that entity
7. return a `SyncResult`

If extraction fails for a page and `hard_fail` is `false`, the service logs the error,
increments the failure counter, and continues.

If persistence fails for a batch and `hard_fail` is `false`, the batch transaction is
rolled back and the entity's failure count is incremented.

## Persistence Behavior

`NotionPersistenceService` is the integration boundary between extracted schemas and ORM
entities.

Important characteristics:

- entities are matched by `notion_page_id`
- new rows are inserted only when no existing entity with that Notion page ID exists
- existing rows are updated in place through the mapper layer
- foreign keys are resolved by looking up related entities using their Notion page IDs
- each entity type flushes before the next dependent type is persisted

This is what makes one-way sync idempotent at the entity identity level.

## Page Content Handling

During sync, the backend attempts to flatten the Notion block tree into plain text and
stores it in `notion_page_content`.

This plain-text body is later surfaced by workout detail/content endpoints and can also
be used by AI prompts without making another Notion request at read time.

## API Entry Point

The integration is exposed through:

- `POST /api/v1/sync/notion`

Query parameter:

- `hard_fail=false` by default

Behavior:

- returns `200` when every entity sync succeeds
- returns `500` with a summary payload when the sync completes but some entities failed
- returns `500` immediately with structured error detail when `hard_fail=true` and the
  first extraction or persistence failure occurs
- returns `503` when rate-limit retries are exhausted
- returns `502` when the downstream Notion API reports authentication, access, or other
  upstream response failures

## Current Design Strengths

- clean separation between fetch, extract, map, and persist
- explicit dependency ordering
- page-content flattening happens during sync rather than at read time
- API-safe summary and error shapes exist for sync consumers
- sync is resilient by default and strict when `hard_fail=true`

## Current Limitations

- sync is one-way only
- writes still start in Notion, not in the backend
- no partial replay per entity through the public API
- no scheduled sync or background job support in v1
- raw external training data still reaches the backend indirectly through Notion

## Practical Guidance

- Use the sync endpoint after setting up a fresh local database.
- Use `hard_fail=true` when debugging extraction or persistence failures.
- Use the default non-strict mode for normal development if you want the aggregate
  summary even when some rows fail.
- Treat `notion_page_id` as the stable identity bridge between Notion and the backend.

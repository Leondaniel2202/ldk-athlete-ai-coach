# API Overview

The current HTTP API is mounted under `/api/v1`.

Important distinction:

- `/api/v1` is the API version
- repository/product "V1" means the current backend milestone described in
  [../releases/v1.md](../releases/v1.md)

Those two version labels are related historically, but they are not the same concept and
should not be treated as interchangeable.

It exposes the current backend in five groups:

- `resources`
- `context`
- `ai`
- `sync`
- `system`

Swagger UI is available at `/docs`.

## API Design Goals

In the current backend milestone, the API is designed to:

- expose mirrored training data from PostgreSQL
- provide richer backend-owned context snapshots beyond raw rows
- support structured AI analysis on top of those context objects
- keep transport contracts explicit with Pydantic schemas

The API is intentionally mostly read-oriented in the current product state.

## Route Groups

## Resources

These endpoints return direct representations or summaries of persisted entities.

### Plans

- `GET /api/v1/resources/plans/{plan_id}`
- `GET /api/v1/resources/plans/{plan_id}/phases`
- `GET /api/v1/resources/plans/{plan_id}/summary`

### Phases

- `GET /api/v1/resources/phases/{phase_id}`
- `GET /api/v1/resources/phases/{phase_id}/workouts`
- `GET /api/v1/resources/phases/{phase_id}/summary`

### Workouts

- `GET /api/v1/resources/workouts/{workout_id}`
- `GET /api/v1/resources/workouts/{workout_id}/content`
- `GET /api/v1/resources/workouts/{workout_id}/details`
- `GET /api/v1/resources/workouts/{workout_id}/sessions`
- `GET /api/v1/resources/workouts/{workout_id}/summary`

### Sessions

- `GET /api/v1/resources/sessions/recent?days=14`
- `GET /api/v1/resources/sessions/{session_id}`
- `GET /api/v1/resources/sessions/{session_id}/summary`

Use the resource routes when the consumer needs the persisted model itself rather than an
analysis-oriented view.

## Context

These endpoints build richer training snapshots using application services.

### Phase Context

- `GET /api/v1/context/phases/{phase_id}`
- `GET /api/v1/context/phases/{phase_id}/weeks?week_start_date=YYYY-MM-DD`

Phase context includes:

- metadata for the evaluation time
- plan summary
- phase status
- phase or phase-week summary
- workouts grouped by role in the context
- adherence and training metrics
- data-gap messages

### Workout Context

- `GET /api/v1/context/workouts/{workout_id}`

Workout context includes:

- metadata for the evaluation time
- plan summary when available
- phase summary when available
- resolved workout status
- detailed workout payload with tracked sessions

Use the context routes when the consumer needs a backend-owned interpretation layer
rather than a single row.

## AI

These endpoints analyze already-structured context through the AI layer.

### Phase Analysis

- `POST /api/v1/ai/analysis/specific-phase-context/{phase_id}`

Request body:

```json
{
  "instruction": "optional additional instruction"
}
```

Response shape:

- `summary`
- `phase_focus`
- `positives`
- `concerns`
- `recommendation`

### Workout Analysis

- `POST /api/v1/ai/analysis/specific-workout-context/{workout_id}`

Request body:

```json
{
  "instruction": "optional additional instruction"
}
```

Response shape:

- `summary`
- `workout_focus`
- `positives`
- `concerns`
- `recommendation`

The AI routes never operate on raw ORM data directly. They first build the same context
objects exposed by the context endpoints and then analyze those.

## Sync

- `POST /api/v1/sync/notion`

Optional query parameter:

- `hard_fail=true|false`

This triggers a blocking, one-way sync from Notion into PostgreSQL and returns an
aggregate summary.

## System

- `GET /api/v1/system/health`

This is the minimal liveness endpoint used for service monitoring and smoke tests.

## Common Response Models

Resource models:

- `PlanResponse`, `PlanSummaryResponse`
- `PhaseResponse`, `PhaseSummaryResponse`
- `WorkoutResponse`, `WorkoutContentResponse`, `WorkoutDetailResponse`, `WorkoutSummaryResponse`
- `SessionResponse`, `SessionSummaryResponse`

Context models:

- `WorkoutContextResponse`
- `PhaseContextResponse`
- `PhaseWeekContextResponse`
- `TrainingMetricsResponse`
- `WorkoutAdherenceSummaryResponse`

AI models:

- `AnalyzePhaseContextRequest`
- `AnalyzePhaseContextResponse`
- `AnalyzeWorkoutContextRequest`
- `AnalyzeWorkoutContextResponse`

## Error Semantics

Common patterns in the current implementation:

- `404` when a requested resource or context root entity does not exist
- `422` for validation failures, including invalid path/query/body data
- `503` for AI configuration/provider failures and Notion rate-limit exhaustion
- `502` for upstream Notion authentication/access/downstream API failures
- `500` for hard-fail sync errors, unexpected sync failures, or partial sync summaries

## How To Use The API

Recommended consumer flow in v1:

1. Sync Notion into the local database.
2. Use resource endpoints to inspect raw entities.
3. Use context endpoints to drive product features or analysis views.
4. Use AI endpoints only when the consumer needs a compact, structured interpretation of
   a context snapshot.

## What The API Does Not Yet Do

- it does not offer first-class write APIs for the training model
- it does not replace Notion as the planning UI
- it does not support AI-driven write workflows
- it does not yet expose advanced analytics or visualization-specific DTOs

# Copilot instructions for this repository

This repository contains a Python backend for an AI coach application.
Follow these instructions for every task in this repo.

## Core principles

* Keep changes small, focused, and easy to review.
* Do not redesign the architecture unless the issue explicitly asks for it.
* Prefer extending the existing structure over introducing new patterns.
* Do not make unrelated changes.
* If a task is unclear, implement only the clearly requested scope.
* For every issue, implement only what is explicitly requested.
* Do not expand scope.
* Do not refactor unrelated code.
* Do not add files unless required by the task.

## Architecture expectations

This repository uses a modular backend design.

Treat these concerns as separate:

* API layer
* application/services layer
* AI integration layer
* persistence/data access layer
* domain/data models
* external integrations

Important boundaries:

* Do not mix API route logic with business logic.
* Do not place database logic directly in API routes.
* Do not place prompt construction logic in API routes.
* Keep external-service-specific logic isolated.
* Keep domain models clean and independent from transport or framework concerns.

## Python standards

* Use Python 3.12+ syntax unless the repository specifies otherwise.
* Prefer explicit, readable code over clever abstractions.
* Use type hints for public functions and important internal functions.
* Keep functions small and focused.
* Prefer dataclasses or Pydantic models where appropriate and consistent with the existing codebase.
* Reuse existing utilities and patterns before adding new helpers.
* Avoid adding unnecessary dependencies.

## Project structure rules

* Put API endpoint changes only in the API layer.
* Put orchestration and use-case logic in service/application modules.
* Put database access in repository or persistence modules.
* Put AI prompt building and model-calling logic in the AI integration layer.
* Put schema/entity definitions in the appropriate domain or model modules.
* Keep configuration in dedicated config/settings modules.

## Development workflow

The Makefile is the canonical interface for developer workflows in this repository.

When implementing tasks or validating changes:

* prefer existing `make` targets over direct tool invocation
* reuse existing targets
* do not invent alternative command flows when a Make target already exists
* do not duplicate commands already present in the Makefile
* do not modify the Makefile unless the task explicitly requires it

## Dependency management

Dependencies are managed with `uv`.

Install dependencies with:

```bash
make install
```

Do not introduce alternative dependency workflows unless explicitly requested.

## Running the API

Run the backend locally with:

```bash
make api
```

## Database

The local development database runs in Docker.

Start the database with:

```bash
make db-up
```

Stop the database with:

```bash
make db-down
```

Database migrations use Alembic.

Apply migrations with:

```bash
make alembic-up
```

Create a migration with:

```bash
make alembic-revision MSG="description"
```

## Code quality and validation

Use the existing Make targets for code validation.

Linting:

```bash
make lint
```

Auto-fix lint issues:

```bash
make lint-fix
```

Formatting check:

```bash
make format-check
```

Type checking:

```bash
make type-check
```

Testing:

```bash
make test
```

## Validation before completing a task

Before considering a task complete, run the relevant existing Make targets if the changed code requires them.

At minimum, prefer these when relevant:

```bash
make lint
make type-check
make test
```

If formatting is part of the task or CI expectations, also run:

```bash
make format-check
```

## Testing expectations

If tests already exist for the affected area:

* update them if needed
* do not ignore failing tests
* do not remove tests unless the issue explicitly requires it

Add or update tests when behavior changes, if the repository already has a testing pattern for that area.

## For GitHub issues

When implementing an issue:

* follow the issue scope strictly
* use the acceptance criteria as the definition of done
* only modify files relevant to the requested task
* do not add extra helpful improvements outside scope

## AI-related implementation rules

For AI features:

* keep prompt construction explicit and inspectable
* prefer structured inputs and outputs
* do not hardcode provider-specific assumptions across the codebase
* keep model/provider interaction behind a dedicated integration layer
* avoid coupling raw external data sources directly to AI prompts when a mapping layer exists

## Database and integration rules

* Do not access the database directly from API routes.
* Do not mix raw external API payloads into domain logic if a mapping or sync layer exists.
* Keep persistence concerns separate from external sync concerns.
* Prefer explicit schema or model mappings over implicit dictionary-based code.

## Documentation expectations

For non-trivial code changes:

* update docstrings or inline comments where they add real value
* keep comments factual and minimal
* do not add obvious comments

## Forbidden unless explicitly requested

* large refactors
* renaming files or modules broadly
* introducing new frameworks
* changing CI/CD behavior
* changing infra or deployment files
* editing unrelated tests
* editing repository structure outside the task

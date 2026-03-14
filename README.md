# ldk-athlete-ai-coach

Minimal backend foundation for the LDK Athlete AI Coach project.

## Planned stack

- Python 3.12
- uv
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- pytest
- ruff
- mypy

## Current status

The repository is being built step by step. The current baseline includes the
Python project configuration, dependency management, and local environment
template. The application scaffold will be added in the next step.

## Local setup

1. Install `uv`.
2. Copy the sample environment file:
   `Copy-Item .env.example .env`
3. Install the project dependencies:
   `uv sync --group dev`

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-14

### Added

- Added Sport Manager SQLAlchemy models from the approved Notion schema, including foreign keys, tracked session-to-workout links, and metadata tests.
- Bootstrapped the Python backend project with `uv`, dependency/tooling configuration, environment defaults, and initial repository documentation.
- Scaffolded the FastAPI application with a `src` layout, root endpoint, versioned API router, and health endpoint.
- Centralized runtime configuration with `pydantic-settings` and added a minimal logging utility for application startup.
- Added the database foundation with PostgreSQL Docker Compose setup, SQLAlchemy base, engine, and session management.
- Introduced Alembic migration infrastructure wired to the application's SQLAlchemy metadata and settings-based database URL.
- Added basic tests covering the root endpoint, health endpoint, and configuration defaults and overrides.
- Added developer workflow commands via `Makefile` and expanded the README with setup, run, quality, and migration instructions.

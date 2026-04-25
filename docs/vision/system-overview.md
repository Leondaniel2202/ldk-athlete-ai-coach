# Product Vision

This document captures the product direction and long-term intent for the system.
It is a strategy document, not the living implementation reference.

For the current implementation, use:

- [Current Architecture](../architecture/current-architecture.md)
- [System Map](../architecture/system-map.md)
- [V1 Release Summary](../releases/v1.md)

## 1. Purpose

The system is a personal training management platform designed to structure, track,
analyze, and improve training over time.

It is being built for real day-to-day use, not as a speculative concept. The goal is
to support current training workflows while steadily evolving toward a more complete
and independent platform.

At its core, the system combines:

- structured training planning
- execution tracking
- analysis and feedback
- AI-assisted interpretation and support

The backend-first approach is intentional. Reliable structure, explicit domain logic,
and clean system boundaries come before advanced frontend or AI behavior.

## 2. Long-Term Direction

The long-term goal is an independent training platform in which the backend owns the
core data model, business logic, analysis, and integrations.

That future platform should provide:

- full control over plans, phases, workouts, sessions, and feedback
- a custom user experience for planning, tracking, and review
- direct ingestion of external training data
- richer analysis of performance, load, consistency, and progression
- AI features grounded in structured history and clear system rules

External systems such as Notion, Apple Health, Strava, or other tools may remain
useful, but they should behave as integrations and data sources rather than core
dependencies.

## 3. Core Product Pillars

### Planning and organization

The system should support clear training structure through plans, phases, workouts,
events, and supporting guidance. It needs enough flexibility to reflect real coaching
and athlete workflows without collapsing into unstructured notes.

### Execution and tracking

The system should capture what actually happened in training, link execution back to
planning, and make it easy to compare intended work against real outcomes.

### Analysis and insight

The system should turn stored training data into useful context, metrics, and trends.
That includes both deterministic calculations and higher-level interpretation.

### Adaptation and coaching support

The system should eventually help adjust training based on missed work, fatigue,
progression, recovery, and constraints. In early stages this may be descriptive and
advisory; later it can become more proactive.

### AI-assisted intelligence

AI should help explain, synthesize, retrieve, and eventually generate useful training
information, but only on top of structured system-owned context.

## 4. Role of AI

AI is an important capability, but it is not the foundation of the product. The
foundation is structured data, explicit domain logic, and stable interfaces.

AI is most valuable in areas such as:

- interpreting free-text notes and feedback
- explaining workout or phase outcomes
- summarizing patterns across training history
- retrieving relevant historical context
- supporting future recommendation and generation workflows

Over time, the system may grow into more advanced AI workflows, including tool-using
or agentic behavior. That should only happen when the surrounding system is reliable
enough to support it safely.

## 5. Guiding Principles

### Stay usable during development

The system should remain useful while it evolves. Transitional states are acceptable
if they support real training use rather than forcing a premature rewrite.

### Structured data first

Core concepts such as plans, phases, workouts, sessions, and feedback should be modeled
explicitly. The system should prefer clear entities and rules over hidden spreadsheet
or document logic.

### Backend ownership grows over time

The backend should increasingly own validation, status logic, metrics, context
building, and integration behavior. Temporary dependence on external tools is
acceptable, but it should shrink over time.

### Separation of concerns matters

Persistence, integration, domain rules, API transport, and AI behavior should remain
separate enough to evolve independently.

### Build for evolution, not novelty

New capabilities should deepen the system rather than replacing it with a different
stack or concept every few months.

### Engineering quality is part of the product

Testing, clear contracts, reproducible setup, migrations, and documentation are part
of the product quality bar, not optional cleanup.

## 6. Evolution Strategy

The system is intentionally evolving in stages instead of attempting an immediate full
replacement of the current workflow.

### Stage 1: backend-first mirror

The current stage mirrors operational training data from Notion into PostgreSQL,
exposes structured APIs, calculates selected backend-owned metrics and statuses, and
adds initial AI analysis on top of structured context.

### Stage 2: increasing backend ownership

More business logic moves into the backend. Validation, calculations, and system rules
become explicit and testable, reducing dependence on Notion formulas and operational
workarounds.

### Stage 3: custom workflow surfaces

A custom frontend can gradually take over key workflows such as planning, review, and
interaction with analysis features.

### Stage 4: direct integrations and richer intelligence

The platform can ingest more data directly, maintain richer history, and support more
advanced analysis, retrieval, and AI-assisted workflows without routing everything
through Notion first.

## 7. Scope

### Current Scope (Product V1)

The current product milestone is a backend-first foundation.

In v1:

- Notion remains the operational source of truth for day-to-day planning and tracking
- the backend mirrors core training entities into PostgreSQL
- selected status and adherence logic is owned by the backend
- FastAPI exposes resource, context, sync, AI, and system endpoints
- AI is limited to structured analysis of backend context
- the system is designed for single-user personal use

### Beyond V1

Beyond v1, the system should move toward:

- backend-owned write workflows
- a custom frontend for daily use
- direct ingestion from external training sources
- richer analytics and visualization
- AI-assisted recommendations, retrieval, and generation
- broader system ownership with less dependency on Notion

The key constraint is that each step should leave the system more coherent, more
trustworthy, and more useful than before.

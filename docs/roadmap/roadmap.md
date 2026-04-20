# Roadmap

## Overview

The system evolves incrementally from a Notion-based training workflow into a fully independent platform.

Each version focuses on a clear objective, ensuring that the system remains usable while gradually increasing its capabilities, ownership, and intelligence.

---

## V1 — Foundation (Completed)

### Goal

Establish a backend foundation that mirrors and structures the existing Notion-based training system.

### Focus Areas

- PostgreSQL database with structured entities
- Notion integration and data synchronization
- Domain modeling of plans, phases, workouts, sessions, and feedback
- Context services (workout, phase week, phase)
- Initial AI analysis capabilities
- FastAPI-based API

### Outcome

A backend system that structures training data and enables analysis, while Notion remains the primary interface and source of truth.

---

## V2 — Usable System Upgrade

### Goal

Introduce a minimal custom frontend for planning and strengthen the backend as the foundation of the system.

### Focus Areas

- Minimal frontend for planning (plans, phases, workouts)
- Backend ownership of core logic (status, metrics, validation)
- Improved API to support frontend interaction
- Continued parallel use of Notion for remaining workflows
- Improved AI analysis and structured outputs

### Outcome

A system where a minimal custom frontend exists for planning experimentation and validation, while Notion remains the primary operational tool and the backend becomes increasingly independent from Notion.

---

## V3 — AI Intelligence Layer

### Goal

Enhance the system’s ability to understand and analyze training through more advanced AI capabilities.

### Focus Areas

- Improved analysis across workouts, weeks, and phases
- Introduction of Retrieval-Augmented Generation (RAG)
- Use of historical training data and feedback for insights
- Structured AI outputs for recommendations and explanations

### Outcome

A system that provides deeper insights and personalized analysis based on both structured data and historical context.

---

## V4 — Adaptation & Agentic AI

### Goal

Enable the system to actively support decision-making and automate parts of the coaching process.

### Focus Areas

- Recommendation systems for training adjustments
- Introduction of tool-based, agentic AI workflows
- Multiple AI “coach” roles (e.g., strength, endurance, recovery)
- Multi-step reasoning and interaction with system APIs

### Outcome

A system that can not only analyze training, but also suggest and orchestrate improvements in a structured and semi-autonomous way.

---

## V5 — Full Independence

### Goal

Achieve full independence from Notion and external workflow dependencies.

### Focus Areas

- Fully developed frontend (web, later mobile)
- Backend as single source of truth
- Direct integration with external data sources (e.g., Apple Health)
- Removal of Notion as operational tool
- Complete ownership of data, logic, and workflows

### Outcome

A fully independent training platform that integrates planning, tracking, analysis, and AI-driven intelligence within a single system.
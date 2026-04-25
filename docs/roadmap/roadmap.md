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

Build the first usable custom application layer on top of the backend by introducing a minimal planning frontend, increasing backend ownership, and making AI a core product capability rather than only an analysis add-on.

### Focus Areas
- Minimal frontend for plans, phases, and workouts
- Backend ownership of status, metrics, validation, and core planning logic
- API maturity for frontend and AI-driven workflows
- Parallel use of Notion for remaining operational workflows
- AI evolution from analysis-only toward personalized, structured coaching support:
    - better analysis
    - athlete context
    - persona-based coaching behavior
    - workout and phase generation
    - initial plan scaffolding

### Outcome

A cohesive system in which frontend, backend, and AI each play an active role: the frontend enables early practical usage, the backend owns core system behavior, and the AI layer supports both understanding and creation of training content while the platform continues progressing toward independence from Notion.

This is based on your current roadmap direction and V2 docs, but adjusted so the AI scope is actually substantial enough for your goals

---

## V3 — AI Context & Intelligence Expansion

### Goal

Expand the system’s intelligence by giving AI access to richer context, stronger grounding, and better-quality reasoning, while continuing the transition away from Notion and maturing the product experience.

### Focus Areas

**AI**

* Introduce Retrieval-Augmented Generation (RAG)
* Expand AI context with:

  * historical training data
  * previous plans, phases, and workouts
  * weekly feedback and reflections
  * external knowledge such as training principles and sports science
* Improve context engineering, evaluation, guardrails, and general AI best practices
* Make AI outputs more robust, explainable, and trustworthy

**Frontend**

* Introduce more advanced product features beyond basic planning
* Add visualizations for training structure, progress, and trends
* Improve presentation of AI insights, recommendations, and generated content
* Create better interfaces for reviewing and working with AI-supported outputs

**Backend**

* Continue moving remaining business logic from Notion into the backend
* Improve backend support for historical analysis and contextual queries
* Begin shifting external data ingestion toward direct system ownership, such as Apple Health integration
* Move closer to working primarily in your own system rather than relying on Notion as the operational layer

### Outcome

A system that can reason over training with much broader context, combining structured history, feedback, and external knowledge, while the frontend becomes more capable and the backend moves closer to full ownership.

---

## V4 — Agentic AI & Adaptive Coaching

### Goal

Turn AI into an active system component that can support decision-making, call tools, and guide coaching workflows in controlled ways, while making the desktop product broadly usable for real day-to-day interaction.

### Focus Areas

**AI**

* Introduce agentic AI workflows
* Enable AI coaches to call tools and interact with system capabilities
* Support multiple coaching roles or personas, such as endurance, strength, and recovery
* Introduce more powerful multi-step reasoning and adaptive decision support
* Build structured action flows so AI can move from analysis to guided action

**Frontend**

* Refine the desktop experience into a broadly usable application
* Improve workflows for reviewing, accepting, adjusting, and applying AI suggestions
* Strengthen product usability, interaction quality, and overall polish

**Backend**

* Support agentic and AI-driven workflows through safer system operations
* Improve write flows, guardrails, constraints, and reliability
* Continue strengthening the backend as the operational core of the system

### Outcome

A system where AI no longer only analyzes or generates content, but actively supports and helps orchestrate coaching decisions through controlled, semi-autonomous workflows.

---

## V5 — Full Platform & Product Expansion

### Goal

Evolve the system into a fully independent training platform with mature product capabilities across devices and deeply integrated AI throughout the experience.

### Focus Areas

**Frontend**

* Introduce a mobile application
* Expand and refine core product features
* Create a unified experience across desktop and mobile
* Continue improving usability, product quality, and completeness

**Backend**

* Complete independence from Notion
* Establish the backend as the single source of truth
* Support direct integrations with external systems and data sources
* Continue improving architecture, stability, and long-term maintainability

**AI**

* Deepen AI integration across the product
* Continue improving analysis, generation, recommendations, and adaptive workflows
* Make AI a natural part of the overall platform experience rather than a separate feature layer

### Outcome

A complete and independent training platform that unifies planning, tracking, analysis, and AI-driven coaching across web and mobile, with full ownership of data, workflows, and user experience.


## Design Notes

These versions intentionally keep all three core pillars moving together:

* **AI** becomes more capable and more deeply integrated
* **Frontend** becomes more usable and more complete
* **Backend** becomes more independent and more operationally central

This keeps the roadmap balanced and avoids overfocusing on AI in a way that would leave the rest of the system behind.

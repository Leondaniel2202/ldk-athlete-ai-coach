## 1. Purpose

This system is a personal training plan management platform designed to structure, track, analyze, and improve training over time.

It is built primarily for direct personal use, with the goal of supporting day-to-day training planning and execution while continuously evolving into a more powerful and independent system.

The system combines:
- structured training planning (plans, phases, workouts)
- real-world execution tracking (sessions, feedback, adherence)
- analytical insights (metrics, trends, balance)
- AI-assisted understanding and decision support

Unlike typical training tools, this system is designed as a backend-first platform with a strong focus on structured data and extensibility, allowing advanced capabilities such as intelligent analysis, recommendations, and future AI-driven workflows.

A key goal is to build a system that remains usable throughout its development, starting from a Notion-based workflow and gradually evolving into a fully independent platform.


## 2. Long-Term Vision

The long-term vision of this system is to evolve into a fully independent training platform that provides complete control over planning, tracking, and analyzing training.

The system will transition from a Notion-based workflow into a standalone application where the backend serves as the single source of truth and a custom frontend provides a seamless user experience across web and mobile.

At its core, the platform aims to become a personal training operating system that:

- centralizes all training data and history
- provides deep insights into performance and progression
- supports structured and flexible planning
- enables intelligent adaptation of training over time

A key aspect of this vision is independence from external tools as core infrastructure. While integrations with systems such as Apple Health or Strava remain important, they should function purely as data sources, not as dependencies for core functionality. The system should be capable of directly ingesting, storing, and processing external data without relying on intermediary platforms.

Another central aspect of this vision is the integration of advanced AI capabilities. The system will incorporate AI not only for analysis and recommendations, but also for more advanced use cases such as:

- retrieving and learning from historical training data (RAG)
- assisting with structured plan and workout generation
- supporting intelligent coaching workflows
- enabling agentic AI systems that can autonomously analyze training and decide how to interact with the system

Despite this long-term ambition, the system is designed to evolve gradually. It will remain usable throughout its development, with existing tools such as Notion being replaced step by step as the platform matures.


## 3. Core Product Pillars

The system is built around a set of core capabilities that define its functionality and long-term value.

### 3.1 Planning & Organization

The system enables structured creation and organization of training:

- Plans, phases, and workouts as core building blocks
- Week-based planning as the primary organizational unit
- Structured workout definitions (e.g., warm-up, main set, cool-down)
- Metadata such as category, purpose, and intensity

The goal is to provide both structure and flexibility, allowing training to be planned even when exact execution details are not yet known.

---

### 3.2 Execution & Tracking

The system captures what actually happens during training:

- Linking planned workouts to tracked sessions
- Recording completion, modification, or skipping of workouts
- Capturing performance data such as duration, distance, and effort
- Storing weekly feedback and qualitative input

This enables a clear comparison between planned and actual training.

---

### 3.3 Analysis & Insight

The system provides structured analysis of training data:

- Weekly (phase week) and phase-level analysis
- Calculation of training load, adherence, and balance
- Identification of patterns, inconsistencies, and potential issues
- Visualization of trends over time (future)

Analysis is based on a combination of deterministic logic (metrics, rules) and AI-assisted interpretation.

---

### 3.4 Adaptation & Coaching

The system supports improving training decisions over time:

- Suggesting adjustments to upcoming training
- Reacting to missed workouts, fatigue, or changing conditions
- Supporting structured progression, deloads, and tapering
- Assisting in aligning training with goals and constraints

This capability evolves from rule-based suggestions toward more advanced AI-supported coaching.

---

### 3.5 AI-Assisted Intelligence

AI is a core capability that enhances the system across multiple areas:

- Interpreting free-text feedback and workout content
- Explaining training outcomes and patterns
- Supporting analysis and recommendations
- Retrieving relevant historical context (RAG)
- Assisting with plan, phase, and workout generation (future)
- Enabling agentic AI workflows that can autonomously interact with the system

AI is designed to augment structured logic, not replace it, and is integrated progressively as the system matures.


## 4. Role of AI

AI is a core capability of the system, but it is intentionally built on top of a structured and well-defined foundation.

The system follows the principle that AI should augment and enhance structured data and deterministic logic, not replace it. Core functionality such as data modeling, metrics calculation, and system constraints are handled explicitly within the backend, ensuring reliability and consistency.

AI is used in areas where interpretation, reasoning, and flexibility provide clear value, including:

- analyzing training at workout, week, and phase level
- interpreting qualitative feedback and notes
- explaining performance trends and outcomes
- suggesting improvements and adjustments to training

The system is designed to progressively incorporate more advanced AI capabilities over time. This includes:

- Retrieval-Augmented Generation (RAG), enabling the system to access and learn from historical training data, workouts, and feedback
- structured generation of training content such as workouts, phases, and plans
- intelligent coaching workflows that combine multiple data sources and reasoning steps

A key long-term goal is the introduction of agentic AI systems. These systems act as “coaches” that are capable of:

- analyzing training context
- deciding which actions to take
- interacting with the system through defined tools and APIs
- orchestrating multi-step reasoning processes

To support this, the system is designed with clear interfaces and structured context outputs, allowing AI components to reliably consume and act upon system data.

AI capabilities are introduced gradually, ensuring that each layer is supported by a strong underlying system and provides real value before adding further complexity.


## 5. Guiding Principles

The system is developed according to a set of guiding principles that ensure long-term quality, usability, and maintainability.

### Usability Throughout Development

The system must remain usable at all stages of its evolution. Decisions should prioritize maintaining or improving the ability to use the system for real training workflows, even if this requires temporary compromises such as parallel use of external tools like Notion.

---

### Structured Data First

A strong and well-defined data model is the foundation of the system. All core concepts such as plans, phases, workouts, sessions, and metrics are explicitly modeled and stored in the backend.

This ensures consistency, reliability, and enables advanced capabilities such as analysis and AI integration.

---

### AI as Augmentation

AI is used to enhance the system, not to replace core logic. Deterministic processes such as data validation, metric calculation, and system constraints are implemented explicitly in the backend.

AI is applied where interpretation, reasoning, and flexibility provide clear value.

---

### Gradual Migration and Independence

The system evolves from a Notion-based workflow to an independent platform in a gradual and controlled way.

External tools may be used temporarily, but the long-term goal is to make the system self-sufficient, with integrations acting only as optional data sources.

---

### Separation of Concerns

The system is structured into clear layers with well-defined responsibilities, including data storage, domain logic, application services, API, and AI components.

This separation enables maintainability, testability, and extensibility.

---

### Build for Evolution

The system is designed to support continuous growth and increasing complexity over time. New capabilities such as advanced analytics, AI features, and frontend components should be added in a way that builds on existing structure rather than replacing it.

---

### Engineering Quality and Best Practices

The system should follow modern engineering best practices, including:

- clean and maintainable code
- proper testing and validation
- clear interfaces and contracts
- type safety and documentation

This ensures that the system remains robust and scalable as it evolves.


## 6. Evolution Strategy

The system is designed to evolve incrementally, ensuring continuous usability while gradually increasing capabilities and independence.

### Parallel System Approach

During early stages, the system operates in parallel with existing tools such as Notion. Notion continues to serve as a practical interface for planning and tracking, while the backend system mirrors, structures, and analyzes the data.

This parallel approach avoids disrupting existing workflows while enabling the gradual transition to a fully independent platform.

---

### Gradual Replacement of Notion

The transition away from Notion is not a single step but a phased process.

- Initial stages focus on replicating and improving core functionality in the backend
- A minimal custom frontend is introduced to cover key planning workflows
- Over time, more functionality is migrated from Notion into the system
- Notion is eventually removed once the custom platform fully supports required workflows

---

### Early Introduction of Frontend

A custom frontend is introduced early in the evolution of the system, with a focus on minimal but practical functionality.

The initial frontend prioritizes:

- planning and organization of training
- usability for day-to-day workflows
- clean structure and best practices

Advanced features such as analytics and AI-driven interactions are added later, once the core functionality is stable.

---

### Progressive AI Integration

AI capabilities are introduced in stages, aligned with the maturity of the system:

1. Structured context and basic analysis
2. Enhanced analysis and interpretation
3. Retrieval-Augmented Generation (RAG) for accessing historical data
4. Structured generation of training content
5. Agentic AI systems capable of autonomous decision-making and tool usage

Each stage builds on a stable foundation, ensuring that AI features provide real value and remain reliable.

---

### Backend Ownership of Logic

Over time, all business logic is moved from external tools into the backend system.

This includes:

- status calculations
- training metrics and load calculations
- aggregation and analysis logic

This transition ensures consistency, transparency, and full control over system behavior.

---

### Direct Data Integration

External data sources such as Apple Health are gradually integrated directly into the system.

Instead of relying on intermediary tools, the system will:

- ingest data directly
- store raw and processed data
- enable more advanced analysis through richer datasets

---

### Continuous Refinement

The system is continuously improved through iteration, including:

- refining data models and constraints
- improving architecture and separation of concerns
- enhancing performance and reliability
- expanding capabilities based on real usage

This iterative approach ensures that the system grows in a controlled and sustainable way.


## 7. Scope

### Current Scope (V1)

The current version of the system is a backend-first foundation that operates alongside a fully functional Notion-based training workflow.

Key characteristics of the current scope include:

- Notion serves as the primary interface for planning, tracking, and basic analysis
- A structured backend system mirrors core data entities such as plans, phases, workouts, sessions, and feedback
- Data is synchronized from Notion into a PostgreSQL database
- Initial domain logic is implemented in the backend, while significant business logic (e.g., metrics and status calculations) עדיין resides in Notion
- Context services provide structured representations of workouts, phase weeks, and phases
- Basic AI capabilities are available for analyzing workout and phase contexts
- The API layer exposes resources, context, and analysis endpoints
- The system is designed for single-user, personal use

---

### Future Scope

The system will expand to become a fully independent platform with significantly broader capabilities, including:

- A custom frontend for planning, tracking, and interaction (web and later mobile)
- Full ownership of data and logic within the backend, removing dependency on Notion
- Direct integration with external data sources such as Apple Health, without intermediary tools
- More advanced and consistent data models with stricter constraints
- Expanded analytical capabilities, including trends, visualizations, and alerts
- AI-assisted analysis, recommendations, and structured generation of training content
- Retrieval-Augmented Generation (RAG) for leveraging historical data and feedback
- Agentic AI systems capable of autonomous reasoning and interaction with system tools
- Support for importing external training plans and transforming them into structured data
- Additional context layers such as athlete profiles, templates, and domain knowledge

The transition from the current scope to the future scope is handled incrementally, ensuring that the system remains usable throughout its evolution.## 7. Scope

### Current Scope (V1)

The current version of the system is a backend-first foundation that operates alongside a fully functional Notion-based training workflow.

Key characteristics of the current scope include:

- Notion serves as the primary interface for planning, tracking, and basic analysis
- A structured backend system mirrors core data entities such as plans, phases, workouts, sessions, and feedback
- Data is synchronized from Notion into a PostgreSQL database
- Initial domain logic is implemented in the backend, while significant business logic (e.g., metrics and status calculations) עדיין resides in Notion
- Context services provide structured representations of workouts, phase weeks, and phases
- Basic AI capabilities are available for analyzing workout and phase contexts
- The API layer exposes resources, context, and analysis endpoints
- The system is designed for single-user, personal use

---

### Future Scope

The system will expand to become a fully independent platform with significantly broader capabilities, including:

- A custom frontend for planning, tracking, and interaction (web and later mobile)
- Full ownership of data and logic within the backend, removing dependency on Notion
- Direct integration with external data sources such as Apple Health, without intermediary tools
- More advanced and consistent data models with stricter constraints
- Expanded analytical capabilities, including trends, visualizations, and alerts
- AI-assisted analysis, recommendations, and structured generation of training content
- Retrieval-Augmented Generation (RAG) for leveraging historical data and feedback
- Agentic AI systems capable of autonomous reasoning and interaction with system tools
- Support for importing external training plans and transforming them into structured data
- Additional context layers such as athlete profiles, templates, and domain knowledge

The transition from the current scope to the future scope is handled incrementally, ensuring that the system remains usable throughout its evolution.
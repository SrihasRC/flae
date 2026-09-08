# CHANGELOG.md — Epistemic Fact-Ledger with Arbitration Engine

All notable changes to this project are documented here. Sub-agents must prepend new entries following the format below upon task completion.

---

## [TASK-02] — 2026-09-08

### Added
- `backend/app/schemas/__init__.py`: Package initialization marker for domain schemas.
- `backend/app/schemas/workspace.py`: Pydantic v2 models for workspace CRUD operations (`WorkspaceCreate`, `WorkspaceRead`, `WorkspaceListResponse`).
- `backend/app/schemas/document.py`: Pydantic v2 models for document metadata, ingestion job status tracking, and upload responses (`DocumentRead`, `DocumentListResponse`, `IngestionJobStatus`, `DocumentUploadResponse`).
- `backend/app/schemas/fact.py`: Canonical Atomic Fact schemas with context qualification envelopes and source evidence citations (`ContextEnvelope`, `Evidence`, `FactCreate`, `FactRead`, `FactListResponse`).
- `backend/app/schemas/arbitration.py`: Cross-document fact arbitration models, evidence comparison, trigger requests, and Case 1–4 explorer schemas (`EvidenceComparison`, `ArbitrationRead`, `ArbitrationListResponse`, `ArbitrationTriggerRequest`, `ArbitrationTriggerResponse`, `CaseExplorerResponse`).

### Modified
- None

### Notes
- Pure Pydantic v2 models with `model_config = ConfigDict(from_attributes=True)` for seamless ORM integration.
- Added pre-validators for enum fields (`period_type`, `entity_scope`, `accounting_methodology`, `relationship`, `status`) to normalize casing and whitespace from LLM extractions.
- Built-in default fallback for `context_envelope` handling in `FactRead` and `FactCreate` to guarantee non-null envelope structure even when database column returns None.

---

## [TASK-01] — 2026-09-08

### Added
- `backend/app/__init__.py`: Package root marker for the backend application.
- `backend/app/core/__init__.py`: Package initialization for the core configuration module.
- `backend/app/core/config.py`: Core application settings using `pydantic-settings` `BaseSettings` loading from `.env` with Chroma configuration and singleton `settings`.
- `backend/app/core/database.py`: Async database session management using SQLAlchemy 2.0 with asyncpg driver, `Base` declarative base, `get_db` async generator dependency, and `init_db` table creation function.

### Modified
- None

### Notes
- Settings automatically resolves `.env` from repository root, backend directory, or current working directory.
- `DATABASE_URL` includes a PostgreSQL async DSN default (`postgresql+asyncpg://postgres:postgres@localhost:5432/fact_ledger`) and automatically normalizes `postgresql://` schemes to `postgresql+asyncpg://`.
- `Base` uses SQLAlchemy 2.0 `DeclarativeBase` for typed `Mapped[]` ORM compatibility.

---

## [ARCHITECT] — 2026-09-08

### Added
- `_context/PLAN.md`: Full 9-task backend engineering roadmap structured into 5 dependency tiers for parallel sub-agent execution. Includes module architecture map, per-task file ownership, step-by-step implementation instructions, and the Parallel Execution Safety Matrix.
- `_context/API_BLUEPRINT.md`: Complete REST API specification with all 15 endpoints, full request/response schemas, pagination conventions, and the Case 1–4 Explorer endpoint. Enables frontend teams to work in parallel.
- `_context/AGENTS.md`: Sub-agent operational handbook governing Git workflow, conflict prevention, coding standards, skill assignments, LLM/vector store integration rules, logging requirements, tier execution gates, post-task routines, and prohibited actions.
- `_context/CHANGELOG.md`: This file. All subsequent task completions must prepend entries here.

### Notes
- Architecture designed for strict parallel safety: 9 tasks across 5 tiers with zero file ownership conflicts.
- `main.py` is locked to TASK-09 only; no other agent may modify it.
- Frontend agents may begin building against `API_BLUEPRINT.md` immediately.


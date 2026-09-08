# CHANGELOG.md — Epistemic Fact-Ledger with Arbitration Engine

All notable changes to this project are documented here. Sub-agents must prepend new entries following the format below upon task completion.

---

## [TASK-03] — 2026-09-08

### Added
- `backend/app/models/__init__.py`: Package initialization marker for database models.
- `backend/app/models/workspace.py`: SQLAlchemy 2.0 ORM model for isolated domain workspaces (`Workspace`) with UUID primary key, unique name index, and timestamp.
- `backend/app/models/document.py`: SQLAlchemy 2.0 ORM model for uploaded PDF documents (`Document`) with foreign key reference to workspaces (ondelete CASCADE), pipeline status, page count, and failure error fields.
- `backend/app/models/fact.py`: SQLAlchemy 2.0 ORM model for extracted atomic facts (`Fact`) with JSONB context envelope and grounded evidence fields, embedding ID reference, and `fact_id` alias interoperability.
- `backend/app/models/arbitration.py`: SQLAlchemy 2.0 ORM model for cross-document fact adjudication records (`Arbitration`) with JSONB evidence comparison, confidence scoring, reasoning trace, and `arbitration_id` alias interoperability.
- `backend/app/repositories/__init__.py`: Package initialization marker for repository layer.
- `backend/app/repositories/workspace_repository.py`: Async repository (`WorkspaceRepository`) providing create, get_by_id, get_by_name, list_all, and delete operations.
- `backend/app/repositories/document_repository.py`: Async repository (`DocumentRepository`) providing create, get_by_id, list_by_workspace, update_status (with facts_extracted and error), count_by_workspace, and delete operations.
- `backend/app/repositories/fact_repository.py`: Async repository (`FactRepository`) providing create_bulk, get_by_id, list_by_workspace (with optional filtering by document, subject, attribute), list_by_document, count_by_workspace, and delete_by_document operations.
- `backend/app/repositories/arbitration_repository.py`: Async repository (`ArbitrationRepository`) providing create_bulk, get_by_id, list_by_workspace (with relationship and min_confidence filters), list_by_relationship, count_by_workspace, and delete_by_workspace operations.

### Modified
- None

### Notes
- All models inherit from `Base` (`DeclarativeBase`) in `app.core.database`.
- PostgreSQL dialect types (`UUID(as_uuid=True)`, `JSONB`) are utilized for canonical schema alignment and fast JSON indexing.
- Both `Fact` and `Arbitration` models include bidirectional property aliases (`fact_id` <-> `id` and `arbitration_id` <-> `id`) and constructor kwargs mapping for seamless Pydantic serialization/deserialization.
- Repositories are asynchronous, accept `AsyncSession`, use SQLAlchemy 2.0 executable statements (`select()`, `delete()`, `func.count()`), and handle UUID string coercion transparently.

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


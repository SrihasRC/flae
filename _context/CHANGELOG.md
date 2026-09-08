# CHANGELOG.md — Epistemic Fact-Ledger with Arbitration Engine

All notable changes to this project are documented here. Sub-agents must prepend new entries following the format below upon task completion.

---

## [TASK-09] — 2026-09-08

### Added
- None

### Modified
- `backend/app/main.py`: Replaced prototype entrypoint with production FastAPI application featuring an `asynccontextmanager` `lifespan` lifecycle (database schema initialization via `init_db()`, non-blocking ChromaDB connectivity check, automatic `uploads/` directory creation), API v1 router mounting at `/api/v1`, and an enhanced `/health` monitoring endpoint reporting database and vector store connectivity states.

### Notes
- ChromaDB connectivity probe in `lifespan` and `/health` runs non-blocking heartbeat checks with lazy imports to ensure application boot resilience even when vector store services are temporarily unreachable.
- Database health check executes lightweight `SELECT 1` queries via isolated `AsyncSessionLocal` contexts.
- All API v1 routes consolidated under `/api/v1` matching the `API_BLUEPRINT.md` specification.

---

## [TASK-08] — 2026-09-08

### Added
- `backend/app/dependencies.py`: FastAPI dependency injection providers for repositories (`WorkspaceRepository`, `DocumentRepository`, `FactRepository`, `ArbitrationRepository`) and services (`ExtractionService`, `EmbeddingService`, `VectorStoreService`, `ArbitrationService`).
- `backend/app/api/__init__.py`: Package initialization marker.
- `backend/app/api/v1/__init__.py`: Package initialization marker for API v1.
- `backend/app/api/v1/endpoints/__init__.py`: Package initialization marker for API v1 endpoints.
- `backend/app/api/v1/endpoints/workspaces.py`: Workspace CRUD endpoints (`POST /`, `GET /`, `GET /{workspace_id}`, `DELETE /{workspace_id}`) with document counting and vector collection deletion.
- `backend/app/api/v1/endpoints/documents.py`: Document upload (`POST /{workspace_id}/documents`), list (`GET /{workspace_id}/documents`), status polling (`GET /{workspace_id}/documents/{document_id}/status`), and deletion (`DELETE /{workspace_id}/documents/{document_id}`), with asynchronous background ingestion pipeline (`run_ingestion_pipeline`) isolated in independent DB sessions.
- `backend/app/api/v1/endpoints/facts.py`: Fact ledger query endpoints (`GET /{workspace_id}/facts`, `GET /{workspace_id}/facts/{fact_id}`) with pagination and filtering by document, subject, and attribute.
- `backend/app/api/v1/endpoints/arbitration.py`: Arbitration execution trigger (`POST /{workspace_id}/arbitration/run`), Case 1-4 Explorer (`GET /{workspace_id}/arbitration/cases`), result listing with filters (`GET /{workspace_id}/arbitration`), and detail retrieval (`GET /{workspace_id}/arbitration/{arbitration_id}`).
- `backend/app/api/v1/router.py`: Centralized v1 router consolidating workspace, document, fact, and arbitration endpoint routers with unified `/workspaces` prefix mapping.

### Modified
- None

### Notes
- Background ingestion pipeline (`run_ingestion_pipeline`) creates dedicated database sessions using `AsyncSessionLocal` to prevent `IllegalStateChangeError` after HTTP response lifecycle completion.
- Pipeline updates status stage-by-stage (`pending` -> `processing` -> `complete` | `failed`), commits status changes immediately, and catches all errors to store traceback summaries in document records.
- `/cases` route in arbitration endpoints is deliberately ordered before `/{arbitration_id}` to prevent FastAPI route evaluation collisions.
- Workspace endpoints accurately query `count_by_workspace` from `DocumentRepository` for live document totals.
- Uploads are saved under `backend/uploads/{workspace_id}/{filename}` with automated folder creation, 50MB size guardrails, and PDF content type validation.

---

## [TASK-07] — 2026-09-08

### Added
- `backend/app/services/arbitration_service.py`: LLM-as-a-Judge arbitration engine adjudicating cross-document fact candidate pairs into CORROBORATED, CONTRADICTED, RECONCILED, or UNRELATED relationships with reasoning traces, evidence juxtaposition, candidate deduplication, and incremental cross-document arbitration.

### Modified
- None

### Notes
- Uses `google-genai` SDK version 2.22.0 (`genai.Client`) with model `gemini-3.8-flash`.
- Employs structured output via `types.GenerateContentConfig` with `ArbitrationOutputSchema` ensuring strict compliance with the REST API and evaluation blueprint.
- Implements single retry on malformed responses or API failures, falling back gracefully to `UNRELATED` with complete evidence preservation and zero system crashes.
- Vector blocking integration uses `vector_store.query_candidates(workspace_id, embedding, exclude_document_id=...)` with default cosine threshold `0.82` and top-K `20`.
- Fact candidate pairs are deduplicated using unordered `frozenset` keys across pairwise iterations to guarantee sub-quadratic execution and zero duplicate Arbiter invocations.
- Incremental mode processes only facts from `new_document_id` against the existing cross-document workspace index.
- Helper `_fact_to_dict` normalizes SQLAlchemy ORM objects, Pydantic models, and dictionaries for transparent repository interoperability.

---

## [TASK-04] — 2026-09-08

### Added
- `backend/app/services/__init__.py`: Package initialization marker for services module.
- `backend/app/services/pdf_parser.py`: Layout-aware PDF ingestion service extracting structured `ParsedBlock` elements (`text`, `table`, `footnote`, `callout`) using `pymupdf4llm`, `pdfplumber`, and `fitz` with footnote binding and stat callout detection.

### Modified
- None

### Notes
- Uses `fitz` (pymupdf) for fast document metadata extraction (`page_count`, `title`, `author`).
- Uses `pymupdf4llm.to_markdown(doc, pages=[i], use_ocr=False)` for high-fidelity markdown layout representation without OCR overhead.
- Integrates `pdfplumber` for table detection, formatting non-redundant tabular blocks to markdown.
- Detects financial stat callouts (isolated numeric/currency-heavy short text blocks < 20 words, such as `₹8,142 Cr` or `740 Mn`).
- Detects bottom-of-page and post-table footnotes (`*`, `†`, `1.`, `2.`, `(1)`, `1/`, etc.) and binds them directly to corresponding table blocks on the same page.
- Fully stateless with zero LLM or database dependencies; all operations performed in-memory from `bytes`.

---

## [TASK-06] — 2026-09-08

### Added
- `backend/app/services/__init__.py`: Package initialization marker for services module.
- `backend/app/services/embedding_service.py`: Semantic embedding service using `google-genai` SDK (`gemini-embedding-2`) with anchor formatting (`subject | attribute`), batch processing (up to 100 anchors), and async support.
- `backend/app/services/vector_store.py`: ChromaDB workspace-partitioned vector index manager with cosine similarity distance metric, candidate retrieval with cross-document filtering, document-level fact purging, and lazy client connection handling.

### Modified
- None

### Notes
- Uses `google-genai` version 2.22.0 (`genai.Client`) with model `gemini-embedding-2`.
- Fact anchor representation is computed as `f"{subject} | {attribute}"`.
- Embeddings are extracted from response via `.embeddings[0].values`.
- `VectorStoreService` wraps `chromadb.HttpClient` initialization with lazy connection recovery to prevent import/startup crashes when the Chroma server is offline.
- Metadata upserted to ChromaDB is automatically sanitized (coercing UUIDs to strings) for type compliance.
- `query_candidates` supports bidirectional parameter ordering (`workspace_id` first or `embedding` first) for robust interoperability.

---

## [TASK-05] — 2026-09-08

### Added
- `backend/app/services/__init__.py`: Package initialization marker for backend domain services.
- `backend/app/services/extraction_service.py`: LLM-powered atomic fact extraction service utilizing `google-genai` (version 2.22.0) with model `gemini-3.8-flash`, structured JSON outputs via Pydantic response schema, batching (up to 10 blocks), tenacity retries, and quote validation hallucination guard (`validate_quote`).

### Modified
- None

### Notes
- Extracted fact schemas conform precisely to canonical specification with `subject`, `attribute`, `value_raw`, `value_numeric`, `unit`, `context_envelope`, `evidence`, `document_id`, and `workspace_id`.
- Implemented `validate_quote(quote, source_text)` with whitespace normalization and smart quote handling, raising Case 4 audit warnings on quote mismatch.
- Extraction service gracefully handles malformed LLM responses with fallback logging and returns empty lists for failed batches without interrupting execution.
- Added tenacity exponential backoff retry logic for LLM API calls.


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


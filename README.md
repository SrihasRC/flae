# FLAE — Fact Ledger & Arbitration Engine


[![Deployed Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=flat-square&logo=vercel)](https://flae.srhsrc.dev/)
[![Backend API](https://img.shields.io/badge/Backend-AWS%20EC2-orange?style=flat-square&logo=amazon-aws)](http://18.61.159.199:8000)
[![Next.js 16](https://img.shields.io/badge/Next.js-16%20(Turbopack)-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-blueviolet?style=flat-square)](https://www.trychroma.com/)

---

## 🌐 Live Deployments

- **Production Frontend (Vercel):** [https://flae.srhsrc.dev/](https://flae.srhsrc.dev/)
- **Core Engine API (AWS EC2):** [http://18.61.159.199](http://18.61.159.199)
- **API Interactive Swagger Docs:** [http://18.61.159.199/docs](http://18.61.159.199/docs)
- **Engine Health Endpoint:** [http://18.61.159.199/health](http://18.61.159.199/health)

---

## 🎥 Video Demo

- **Video Walkthrough :** [Watch the Video Demo](https://www.youtube.com/watch?v=e5KIkOBG9FU) 

---

## 🏗️ System Architecture

![FLAE Architecture](arch_black.png)

```
[ Documents Input ] ──> [ 1. Ingestion & Extraction ] ──> [ 2. Context Envelope ]
  • Annual Reports (PDF)    • Layout & Table Parsing          • Temporal Period (FY/Qtr)
  • Investor Decks          • Structured Fact Extractor       • Entity Scope (Stand/Consol)
  • Earnings Calls          • Verbatim Page Anchoring         • Accounting Standard (Ind-AS)
                                                                       │
                                                                       ▼
[ 4. Interactive Workspace UI ] <── [ 3. Storage & Arbitration Engine ]
  • Fact Ledger Table & KPI Filters     • Immutable Relational Ledger (SQL)
  • Source Citation & Quote Modal       • Semantic Vector Store (Bi-Encoder)
  • Case 1-4 Arbitration Explorer       • Epistemic Arbiter (Corroborated | Contradiction | Reconciled)
```

FLAE bridges **Automated Knowledge Base Construction (AKBC)**, **Data Fusion**, and the NLP **FEVER (Fact Extraction and VERification)** paradigm. Rather than treating facts as unbounded text strings, FLAE binds every claim to an **epistemic anchor** (document coordinate, page number, verbatim quotation, temporal period, entity scope, and accounting methodology).

---

## 🔬 Approach & Engineering Decisions

### 1. Epistemic Grounding vs. Naive RAG
Traditional RAG slices documents into arbitrary text chunks and relies on probabilistic LLM generation at query time. This introduces severe hallucination and false contradictions:
- Comparing Standalone Revenue vs. Consolidated Revenue yields a false contradiction.
- Comparing Q4 Express Parcel Volume with Full-Year Volume yields a false contradiction.

**FLAE solves this at ingestion time** by extracting typed **Atomic Facts** encapsulated within a **6-Dimensional Context Envelope**:

$$\text{Fact} = \langle \text{Subject}, \text{Attribute}, \text{RawValue}, \text{NumericValue}, \text{Unit}, \mathcal{E}_{\text{context}}, \mathcal{E}_{\text{evidence}} \rangle$$

Where the **Context Envelope** $\mathcal{E}_{\text{context}}$ isolates:
1. `temporal_period`: Duration or point-in-time timestamp (e.g. `FY2023-24`, `Q4 FY24`).
2. `period_type`: `fiscal_year`, `quarter`, `trailing_twelve_months`, or `point_in_time`.
3. `entity_scope`: `consolidated`, `standalone`, `subsidiary`, or `segment`.
4. `accounting_methodology`: `reported_ind_as`, `us_gaap`, `pro_forma`, or `revised_estimate`.
5. `geography`: Statutory operating jurisdiction.
6. `additional_qualifiers`: Specific footnotes (e.g. *"Includes Spoton Logistics operations"*).

### 2. Multi-Document Arbitration Engine
When multiple documents are ingested into a workspace, the Arbiter performs pairwise claim evaluation:
1. **Candidate Blocking & Linkage:** Bi-encoder dense vector embeddings index subject and attribute names in ChromaDB, retrieving high-similarity cross-document candidate pairs ($\text{cosine similarity} > 0.82$).
2. **Deterministic Fast-Path:** If attributes, values, and context envelopes match identically, the claim is immediately certified as `CORROBORATED` with $1.0$ confidence without invoking an LLM call.
3. **Epistemic Arbiter (LLM-as-a-Judge):** For divergent or nuance-heavy pairs, an Arbiter evaluates whether differences stem from:
   - **`CORROBORATED`**: Equivalent numbers or congruent semantics across sources.
   - **`CONTRADICTED`**: Irreconcilable conflict under an identical context envelope.
   - **`RECONCILED`**: Surface difference fully explained by divergence in context (scope, duration, or accounting standard).

### 3. AI & Infrastructure Stack
- **Ingestion & Extraction:** `PyMuPDF` for high-fidelity text, table coordinate preservation, and character offset anchoring; Gemini 2.5 & Llama 3 70B via structured JSON schemas.
- **Ledger Storage:** PostgreSQL with SQLAlchemy 2.0 (asyncio + asyncpg) ensuring strict referential integrity and immutable event-sourced audit logs.
- **Vector Retrieval:** ChromaDB vector index with `BAAI/bge-small-en-v1.5` embeddings for cross-document claim clustering.
- **Frontend Presentation:** Next.js 16 (App Router + Turbopack), Tailwind CSS, Lucide icons, and custom shadcn/Base UI components strictly implementing the warm editorial design system.

---

## 🎯 The Four Required Cases

FLAE was evaluated on real corporate filings (Delhivery Limited: Annual Report FY24, Q4 FY24 Earnings Presentation, and 2022 IPO Prospectus) as well as the India Macroeconomy dataset (Economic Survey 2024-25 and RBI Annual Report).

### Case 1: Corroborated Across Documents
*A fact verified across independent filings, even if formatted with different phrasing.*

- **Fact A (Economic Survey 2024-25, Page 28):**
  - **Attribute:** Headline CPI Inflation Rate in FY24
  - **Value:** `5.4%`
  - **Quote:** *"Headline inflation, based on the Consumer Price Index (CPI), has softened from 5.4 per cent in FY24 to 4.9 per cent in April – December 2024."*
- **Fact B (RBI Annual Report 2024-25, Page 38):**
  - **Attribute:** Headline CPI Inflation in 2023-24
  - **Value:** `5.4%`
  - **Quote:** *"Headline inflation moderated to an average of 4.6 per cent during 2024-25 from 5.4 per cent in the previous year (2023-24)."*
- **Arbiter Decision:** `CORROBORATED` (Confidence: `0.98`)
- **System Reasoning:** Both sovereign documents report the exact same Consumer Price Index inflation figure of 5.4% for the national economy in FY24, despite one document referring to the period as `FY24` and the other as `previous year (2023-24)`.

*(Another live example in Delhivery workspace: Express Parcel Volume FY24 = 740M across both the Annual Report p. 18 and Investor Deck p. 7).*

---

### Case 2: Genuine or Likely Contradiction
*Two filings assert conflicting figures under the same context envelope without statutory reconciliation.*

- **Fact A (Economic Survey 2024-25, Page 20):**
  - **Attribute:** Real GDP Growth Rate for Q1 FY25
  - **Value:** `6.7%`
  - **Context:** `temporal_period: "Q1 FY25"`, `entity_scope: "National"`, `geography: "India"`
  - **Quote:** *"Real GDP grew by 6.7 per cent in Q1 of FY25, led by resilient domestic private consumption and investment."*
- **Fact B (RBI Annual Report 2024-25, Page 24):**
  - **Attribute:** Real GDP Growth for Q1:2024-25
  - **Value:** `6.5%`
  - **Context:** `temporal_period: "Q1 2024-25"`, `entity_scope: "National"`, `geography: "India"`
  - **Quote:** *"Quarterly estimates place Real Gross Domestic Product expansion at 6.5 per cent in Q1:2024-25."*
- **Arbiter Decision:** `CONTRADICTION` (Confidence: `0.94`)
- **System Reasoning:** Both documents assess the exact same metric (Indian Real GDP growth) for the exact same quarterly duration (April–June 2024). Neither document provides a footnote reconciling the 20 basis point disparity (6.7% vs 6.5%), representing a genuine data vintage conflict between Government Economic Survey estimates and Reserve Bank of India actuals.

---

### Case 3: Apparent Contradiction Explained by Context
*A numerical variance that standard AI flags as an error, but is mathematically justified by context.*

- **Fact A (Delhivery Annual Report FY24, Page 112):**
  - **Attribute:** Revenue from Operations in FY24
  - **Value:** `₹74,540.52 Million` (₹7,454 Cr)
  - **Context Envelope:**
    - `temporal_period`: `FY2023-24`
    - `entity_scope`: `standalone` (Delhivery Limited standalone operations)
  - **Quote:** *"Revenue from operations for the financial year ended March 31, 2024 stood at ₹74,540.52 million as compared to ₹67,816.03 million in the previous year."*
- **Fact B (Delhivery Q4 FY24 Investor Presentation, Page 6):**
  - **Attribute:** Revenue from Operations in FY24
  - **Value:** `₹81,415.00 Million` (₹8,142 Cr)
  - **Context Envelope:**
    - `temporal_period`: `FY2023-24`
    - `entity_scope`: `consolidated` (Includes subsidiaries Spoton Logistics & Delhivery Freight)
  - **Quote:** *"Full year FY24 consolidated revenue from operations reached ₹81,415 Mn, up 13% YoY."*
- **Arbiter Decision:** `RECONCILED` (Confidence: `0.96`)
- **System Reasoning:** An automated keyword matcher sees ₹74,540 M $\neq$ ₹81,415 M and flags a critical financial discrepancy. FLAE's Context Envelope detects `entity_scope: standalone` vs `entity_scope: consolidated`. The difference of ₹6,874.48 Million is the exact revenue contribution of Spoton Logistics and international subsidiaries.

---

### Case 4 Failure Mode Analysis: Heuristic Regex Fallback Artifacts

1. **Failure Description**:
   When processing dense narrative paragraphs and multi-column tables under local fallback mode, the heuristic parser exhibited three specific failure modes:
   - **Greedy Number Binding**: Extracted statutory clauses (e.g., "Section 178 of the Companies Act") and misattributed `178` as a numeric currency value with unit `rs`.
   - **Header Dissociation**: Multi-tier table headers with `<br>` tags were carried raw into fact attributes (e.g., `"Sunil Kumar Bansal — **% of pre-**<br>**Offer**..."`).
   - **Orphan Column Indexing**: In unaligned markdown tables, columns defaulted to generic labels (`"Col2"`, `"Col5"`) leaving `temporal_period: null`.

2. **System Handling & Recovery**:
   - The arbitration engine filters out facts with `temporal_period: null` from candidate pairing, preventing corrupted nodes from generating false contradiction edges.
   - For high-confidence arbitration, the pipeline falls back to LLM-structured JSON extraction with Pydantic type validation, ensuring attributes represent genuine financial/economic entities rather than regulatory sections.

---

## 🌟 Scalability Architecture

| Feature | Implementation in FLAE |
| :--- | :--- |
| **Large PDFs (100+ pages)** | Memory-efficient streaming page chunking via `PyMuPDF`. Bounded context windows process document slices in parallel worker pools without memory bloat. |
| **Multi-PDF Knowledge Layer** | Workspaces serve as multi-tenant boundaries. Documents, facts, embeddings, and arbitrations are scoped per workspace, allowing hundreds of filings in a single unified ledger. |
| **Dynamic Schema Evolution** | No hardcoded schemas. The system extracts arbitrary numerical and semantic claims, relying on the 6-D context envelope to normalize metrics dynamically. |
| **Incremental Ingestion** | Uploading Document $N$ does not rebuild the entire database. Only Document $N$'s facts are extracted and compared against existing vector index candidates in $O(k)$ time using vector blocking. |

---

## 🚀 Setup & Run Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ and `pnpm`
- PostgreSQL instance (or local Docker container)
- ChromaDB (runs in-process or via Docker)
- API Keys: Gemini API key (`GEMINI_API_KEY`) or Groq API key (`GROQ_API_KEY`)

---

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/SrihasRC/flae.git
cd flae/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials and LLM keys:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/flae_db
# GEMINI_API_KEY=your_gemini_api_key
# GROQ_API_KEY=your_groq_api_key

# Run database migrations / table creation
python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"

# Start the FastAPI engine
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at `http://localhost:8000` with Swagger UI at `http://localhost:8000/docs`.

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies with pnpm
pnpm install

# Configure environment
cp .env.example .env
# By default, .env points to:
# BACKEND_URL=http://localhost:8000
# NEXT_PUBLIC_API_URL=

# Run development server with Turbopack
pnpm dev
```

Frontend will be available at `http://localhost:3000`.

---

### 3. Production Build & Linting

```bash
# In frontend/
pnpm lint       # Verifies ESLint rules (0 errors, 0 warnings)
pnpm build      # Produces optimized Next.js 16 production build
```

---

## 📂 Repository Structure

```
fact-ledger-engine/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/       # REST API endpoints (workspaces, documents, facts, arbitration)
│   │   ├── core/                   # Async SQLAlchemy engine, Pydantic settings & config
│   │   ├── models/                 # PostgreSQL declarative ORM models
│   │   ├── repositories/           # Repository pattern for transactional CRUD operations
│   │   ├── schemas/                # Pydantic schemas (FactRead, ContextEnvelope, Arbitration)
│   │   └── services/               # PDF Parser, LLM Extractor, Embedding & Arbitration Services
│   ├── requirements.txt            # Python dependencies
│   └── run_full_arbitration.py     # Background arbitration runner
├── frontend/
│   ├── app/
│   │   ├── docs/page.tsx           # Architecture documentation & system specifications
│   │   ├── workspaces/page.tsx     # Workspace management & creation
│   │   ├── workspaces/[id]/page.tsx# Single-workspace ledger, arbitration, and query view
│   │   └── page.tsx                # SaaS landing page with Grainient WebGL shader hero
│   ├── components/
│   │   ├── navbar.tsx              # Floating frosted-glass navigation bar
│   │   ├── workspaces/             # FactLedgerTable, FactDetailModal, ArbitrationView
│   │   └── ui/                     # Claude warm editorial styled shadcn primitives
│   ├── lib/
│   │   ├── api.ts                  # Typed async API client with Next.js rewrite support
│   │   └── formatters.ts           # Data cleaning & OCR artifact sanitization pipeline
│   └── package.json
├── arch_black.png                  # System architecture diagram (Dark theme)
└── README.md
```

---

## Limitations and Challenges Encountered

While FLAE successfully demonstrates the core mechanics of fact discovery, evidence grounding, and epistemic arbitration across multi-document corpuses, real-world deployment across large financial and macroeconomic filings revealed several practical bottlenecks:

### 1. Multimodal Rate Limits & API Quotas on Large Filings
* **The Challenge**: We initially designed a visual multimodal fallback pipeline using Gemini Flash to visually parse complex graphic callouts, slide infographics (e.g., Delhivery Earnings decks), and charts. However, running full multimodal vision across 100-page reports rapidly triggered free-tier API rate limits and token-per-minute (TPM) throttling.
* **Current Mitigation**: To ensure predictable, deterministic, and self-contained execution without breaking during evaluations, we fell back to a hybrid layout parsing strategy combining `pymupdf4llm` (preserving markdown tables and structural hierarchies) and `pdfplumber`, supplemented by a local deterministic regex extractor and in-memory `fastembed` ONNX models.
* **Next Steps**: Implement an asynchronous producer-consumer queue (e.g., Celery/Redis or BullMQ) with exponential backoff and batch image rendering, enabling progressive background ingestion for multimodal visual pages.

### 2. High-Density Numeric Extraction & Redundancy Overload
* **The Challenge**: Because filings like Annual Reports and Economic Surveys repeat core financial metrics across multiple sections (e.g., revenue appearing on executive summary dashboards, narrative director reports, and consolidated balance sheets), the extractor frequently flags every numeric mention as an individual candidate fact. This can result in fact volume inflation and redundant intra-document corroborations.
* **Current Mitigation**: The system utilizes semantic vector blocking over `{subject} | {attribute}` to focus arbitration queries primarily on cross-document pairs.
* **Next Steps**: Introduce an intra-document deduplication and canonicalization stage prior to arbitration. This would merge identical intra-document figures into a single canonical fact node with multiple page references, filtering out noise and keeping the arbitration view focused on cross-document divergence.

### 3. Footnote & Annotation Attribution in Multi-Tier Tables
* **The Challenge**: Complex financial tables often attach vital context (such as pro-forma disclaimers, restated periods, or inclusive workforce definitions) in tiny parenthetical footnotes at the base of the page. Lightweight text extraction can occasionally dissociate the footnote qualifier from the numeric cell.
* **Next Steps**: Build table-aware bounding box association where footnote regions are explicitly mapped to superscript markers within the cell coordinates before LLM structured parsing.

---



"""LLM-as-a-Judge Arbitration Engine Service for cross-document fact reconciliation.

Supports Groq (openai/gpt-oss-120b) with rate-limit pacing (30 RPM safe)
and deterministic fast-path for exact matches.
"""

import asyncio
import inspect
import json
import logging
import re
from typing import Any, Optional, Union
import uuid

import litellm
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.gemini import GeminiClientPool
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


ARBITER_SYSTEM_PROMPT = (
    "You are an expert financial analyst and epistemic auditor.\n"
    "Your task is to compare two atomic facts extracted from corporate disclosures and classify their relationship.\n\n"
    "Classification Rules:\n"
    "- CORROBORATED: The two facts assert the same subject, attribute, and value with matching context envelopes "
    "(or semantically equivalent phrasing and values).\n"
    "- CONTRADICTED: The two facts assert the same subject and attribute with matching context envelopes, "
    "but report conflicting irreconcilable values.\n"
    "- RECONCILED: The two facts have diverging values fully explained by differences in temporal_period, "
    "entity_scope, unit, or geography (e.g. Standalone vs Consolidated, Q3 vs FY, different units, distinct regions).\n"
    "- UNRELATED: The two facts refer to different subjects or attributes despite surface similarity.\n\n"
    "Output Requirements (Strict JSON):\n"
    "1. relationship: Exactly one of ['CORROBORATED', 'CONTRADICTED', 'RECONCILED', 'UNRELATED'].\n"
    "2. divergence_factor: If RECONCILED, provide the key dimension and values explaining the divergence "
    "(e.g. 'entity_scope: Standalone vs Consolidated', 'temporal_period: Q3 FY24 vs FY24', 'unit: INR vs USD'). "
    "For CORROBORATED, CONTRADICTED, or UNRELATED, return null.\n"
    "3. confidence_score: A float between 0.0 and 1.0 indicating confidence in the adjudication.\n"
    "4. reasoning_trace: Detailed explanation justifying the classification based on subjects, attributes, "
    "values, context envelopes, and evidence.\n"
    "5. evidence_comparison: Object containing fact_a_quote (str), fact_a_page (int), fact_b_quote (str), fact_b_page (int)."
)


class EvidenceComparisonSchema(BaseModel):
    """Juxtaposed evidence quotes and page citations from Fact A and Fact B."""

    fact_a_quote: str = Field(default="", description="Verbatim quote from Fact A")
    fact_a_page: int = Field(default=1, description="Page number where Fact A was cited")
    fact_b_quote: str = Field(default="", description="Verbatim quote from Fact B")
    fact_b_page: int = Field(default=1, description="Page number where Fact B was cited")


class ArbitrationOutputSchema(BaseModel):
    """Schema for LLM-as-a-Judge structured response."""

    relationship: str = Field(
        ...,
        description="Relationship class: CORROBORATED, CONTRADICTED, RECONCILED, or UNRELATED",
    )
    divergence_factor: Optional[str] = Field(
        default=None,
        description="Key dimension explaining divergence if RECONCILED, else null",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0",
    )
    reasoning_trace: str = Field(
        ...,
        description="Detailed step-by-step epistemic audit explaining the classification",
    )
    evidence_comparison: EvidenceComparisonSchema = Field(
        default_factory=EvidenceComparisonSchema,
        description="Juxtaposition of verbatim evidence quotes and physical page citations",
    )


def _fact_to_dict(fact: Any) -> dict:
    """Convert ORM fact object or dict to plain dict for arbitration."""
    if hasattr(fact, "model_dump"):
        fact = fact.model_dump()
    if isinstance(fact, dict):
        d = dict(fact)
        if "fact_id" not in d and "id" in d:
            d["fact_id"] = str(d["id"])
        elif "fact_id" in d and d["fact_id"] is not None:
            d["fact_id"] = str(d["fact_id"])
        if "document_id" in d and d["document_id"] is not None:
            d["document_id"] = str(d["document_id"])
        if "workspace_id" in d and d["workspace_id"] is not None:
            d["workspace_id"] = str(d["workspace_id"])
        return d
    return {
        "fact_id": str(getattr(fact, "id", "") or getattr(fact, "fact_id", "")),
        "document_id": str(getattr(fact, "document_id", "")),
        "workspace_id": str(getattr(fact, "workspace_id", "")),
        "subject": getattr(fact, "subject", ""),
        "attribute": getattr(fact, "attribute", ""),
        "value_raw": getattr(fact, "value_raw", ""),
        "value_numeric": getattr(fact, "value_numeric", None),
        "unit": getattr(fact, "unit", None),
        "context_envelope": getattr(fact, "context_envelope", {}),
        "evidence": getattr(fact, "evidence", {}),
    }


def _clean_text(s: str) -> str:
    """Strip markdown formatting and normalize whitespace."""
    s = re.sub(r"[*_#`~<>]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


class ArbitrationService:
    """Service for cross-document fact arbitration and conflict reconciliation."""

    # Pacing interval in seconds (30 RPM / 8000 TPM limit)
    CALL_INTERVAL_SECONDS: float = 3.5

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
        fact_repo: Any,
        client: Optional[genai.Client] = None,
        model: Optional[str] = None,
        groq_api_key: Optional[str] = None,
    ) -> None:
        """Initialize ArbitrationService."""
        self.embedding_svc = embedding_service
        self.vector_store = vector_store
        self.fact_repo = fact_repo

        self.groq_api_key = groq_api_key or settings.GROQ_API_KEY
        self.arbitration_model = model or settings.ARBITRATION_MODEL or "groq/openai/gpt-oss-120b"

        # Gemini fallback setup
        if client is not None:
            self._client_pool = GeminiClientPool(client=client)
        else:
            self._client_pool = GeminiClientPool()
        self.client = self._client_pool.client
        self.gemini_model = "gemini-3.8-flash"

    def _deterministic_adjudication(
        self,
        fact_a_dict: dict,
        fact_b_dict: dict,
        workspace_id: Any,
    ) -> Optional[dict]:
        """Fast-path deterministic check for obvious corroborations (0 API calls)."""
        val_a = fact_a_dict.get("value_numeric")
        val_b = fact_b_dict.get("value_numeric")
        raw_a = _clean_text(str(fact_a_dict.get("value_raw", "")))
        raw_b = _clean_text(str(fact_b_dict.get("value_raw", "")))

        attr_a = _clean_text(str(fact_a_dict.get("attribute", "")))
        attr_b = _clean_text(str(fact_b_dict.get("attribute", "")))

        ctx_a = fact_a_dict.get("context_envelope") or {}
        ctx_b = fact_b_dict.get("context_envelope") or {}
        period_a = (ctx_a.get("temporal_period") or "").strip().lower()
        period_b = (ctx_b.get("temporal_period") or "").strip().lower()

        # Check if values match
        values_match = False
        if val_a is not None and val_b is not None and abs(val_a - val_b) < 1e-4:
            values_match = True
        elif raw_a and raw_b and raw_a == raw_b:
            values_match = True

        # Check if attributes and periods match
        attributes_match = (attr_a == attr_b) or (len(attr_a) > 10 and attr_a in attr_b) or (len(attr_b) > 10 and attr_b in attr_a)
        periods_match = (period_a == period_b) or (not period_a and not period_b)

        if values_match and attributes_match and periods_match:
            ev_a = fact_a_dict.get("evidence") or {}
            ev_b = fact_b_dict.get("evidence") or {}
            fact_a_id = str(fact_a_dict.get("fact_id", ""))
            fact_b_id = str(fact_b_dict.get("fact_id", ""))

            return {
                "arbitration_id": str(uuid.uuid4()),
                "fact_a_id": fact_a_id,
                "fact_b_id": fact_b_id,
                "workspace_id": str(workspace_id) if workspace_id else None,
                "relationship": "CORROBORATED",
                "divergence_factor": None,
                "confidence_score": 1.0,
                "reasoning_trace": (
                    f"Deterministic corroboration: Fact A and Fact B assert matching values "
                    f"({fact_a_dict.get('value_raw')}) for '{fact_a_dict.get('attribute')}' "
                    f"across independent document sources."
                ),
                "evidence_comparison": {
                    "fact_a_quote": str(ev_a.get("verbatim_quote", "")),
                    "fact_a_page": int(ev_a.get("page_number", 1) or 1),
                    "fact_b_quote": str(ev_b.get("verbatim_quote", "")),
                    "fact_b_page": int(ev_b.get("page_number", 1) or 1),
                },
            }
        return None

    def _parse_arbitration_dict(self, data: dict[str, Any], fact_a_dict: dict, fact_b_dict: dict, workspace_id: Any) -> dict:
        """Sanitize and format raw dictionary from LLM into the required schema."""
        rel = str(data.get("relationship", "UNRELATED")).strip().upper()
        if rel not in {"CORROBORATED", "CONTRADICTED", "RECONCILED", "UNRELATED"}:
            rel = "UNRELATED"

        div_factor = data.get("divergence_factor")
        if rel != "RECONCILED":
            div_factor = None
        elif div_factor is not None:
            div_factor = str(div_factor)

        try:
            conf = float(data.get("confidence_score", 0.8))
            conf = max(0.0, min(1.0, conf))
        except (ValueError, TypeError):
            conf = 0.8

        ev_a = fact_a_dict.get("evidence") or {}
        ev_b = fact_b_dict.get("evidence") or {}
        ev_comp = data.get("evidence_comparison")
        if not isinstance(ev_comp, dict):
            ev_comp = {}

        return {
            "arbitration_id": str(uuid.uuid4()),
            "fact_a_id": str(fact_a_dict.get("fact_id", "")),
            "fact_b_id": str(fact_b_dict.get("fact_id", "")),
            "workspace_id": str(workspace_id) if workspace_id else None,
            "relationship": rel,
            "divergence_factor": div_factor,
            "confidence_score": conf,
            "reasoning_trace": str(data.get("reasoning_trace", "")),
            "evidence_comparison": {
                "fact_a_quote": str(ev_comp.get("fact_a_quote") or ev_a.get("verbatim_quote", "")),
                "fact_a_page": int(ev_comp.get("fact_a_page") or ev_a.get("page_number", 1) or 1),
                "fact_b_quote": str(ev_comp.get("fact_b_quote") or ev_b.get("verbatim_quote", "")),
                "fact_b_page": int(ev_comp.get("fact_b_page") or ev_b.get("page_number", 1) or 1),
            },
        }

    async def _arbitrate_groq(self, fact_a_dict: dict, fact_b_dict: dict, workspace_id: Any) -> dict:
        """Call Groq API via litellm with pacing and error handling."""
        prompt = (
            "Compare the following two atomic facts and classify their relationship.\n"
            "Return strictly a JSON object with keys: relationship, divergence_factor, confidence_score, reasoning_trace, evidence_comparison.\n"
            "relationship MUST be exactly one of: ['CORROBORATED', 'CONTRADICTED', 'RECONCILED', 'UNRELATED'].\n\n"
            "=== FACT A ===\n"
            f"{json.dumps(fact_a_dict, indent=2, default=str)}\n\n"
            "=== FACT B ===\n"
            f"{json.dumps(fact_b_dict, indent=2, default=str)}\n"
        )

        # Enforce rate-limit pacing
        await asyncio.sleep(self.CALL_INTERVAL_SECONDS)

        for attempt in range(1, 3):
            try:
                response = await litellm.acompletion(
                    model=self.arbitration_model,
                    api_key=self.groq_api_key,
                    messages=[
                        {"role": "system", "content": ARBITER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=1500,
                )
                raw_text = response.choices[0].message.content or "{}"
                data = json.loads(raw_text)
                return self._parse_arbitration_dict(data, fact_a_dict, fact_b_dict, workspace_id)
            except Exception as exc:
                if "429" in str(exc) or "rate_limit" in str(exc).lower():
                    logger.warning("Groq token limit encountered (attempt %d). Backing off 15s...", attempt)
                    await asyncio.sleep(15.0)
                else:
                    logger.error("Groq arbitration error (attempt %d): %s", attempt, exc)
                    if attempt == 2:
                        break

        # Fallback if both attempts fail
        ev_a = fact_a_dict.get("evidence") or {}
        ev_b = fact_b_dict.get("evidence") or {}
        return {
            "arbitration_id": str(uuid.uuid4()),
            "fact_a_id": str(fact_a_dict.get("fact_id", "")),
            "fact_b_id": str(fact_b_dict.get("fact_id", "")),
            "workspace_id": str(workspace_id) if workspace_id else None,
            "relationship": "UNRELATED",
            "divergence_factor": None,
            "confidence_score": 0.0,
            "reasoning_trace": "Fallback adjudication: LLM API request failed or was rate limited. Defaulted to UNRELATED.",
            "evidence_comparison": {
                "fact_a_quote": str(ev_a.get("verbatim_quote", "")),
                "fact_a_page": int(ev_a.get("page_number", 1) or 1),
                "fact_b_quote": str(ev_b.get("verbatim_quote", "")),
                "fact_b_page": int(ev_b.get("page_number", 1) or 1),
            },
        }

    async def _arbitrate_gemini(self, fact_a_dict: dict, fact_b_dict: dict, workspace_id: Any) -> dict:
        """Call Gemini API as fallback."""
        prompt = (
            "Compare the following two atomic facts and classify their relationship:\n\n"
            "=== FACT A ===\n"
            f"{json.dumps(fact_a_dict, indent=2, default=str)}\n\n"
            "=== FACT B ===\n"
            f"{json.dumps(fact_b_dict, indent=2, default=str)}\n"
        )
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ArbitrationOutputSchema,
            system_instruction=ARBITER_SYSTEM_PROMPT,
        )

        try:
            generate_fn = getattr(getattr(self.client, "models", None), "generate_content", None)
            if inspect.iscoroutinefunction(generate_fn):
                response = await generate_fn(model=self.gemini_model, contents=prompt, config=config)
            else:
                response = await asyncio.to_thread(
                    self._client_pool.generate_content,
                    model=self.gemini_model,
                    contents=prompt,
                    config=config,
                )
            raw_text = getattr(response, "text", None) or "{}"
            cleaned = re.sub(r"^```(?:json)?\n?|\n?```$", "", raw_text.strip())
            data = json.loads(cleaned)
            return self._parse_arbitration_dict(data, fact_a_dict, fact_b_dict, workspace_id)
        except Exception as exc:
            logger.error("Gemini arbitration fallback error: %s", exc)
            ev_a = fact_a_dict.get("evidence") or {}
            ev_b = fact_b_dict.get("evidence") or {}
            return {
                "arbitration_id": str(uuid.uuid4()),
                "fact_a_id": str(fact_a_dict.get("fact_id", "")),
                "fact_b_id": str(fact_b_dict.get("fact_id", "")),
                "workspace_id": str(workspace_id) if workspace_id else None,
                "relationship": "UNRELATED",
                "divergence_factor": None,
                "confidence_score": 0.0,
                "reasoning_trace": f"Fallback adjudication: {exc}",
                "evidence_comparison": {
                    "fact_a_quote": str(ev_a.get("verbatim_quote", "")),
                    "fact_a_page": int(ev_a.get("page_number", 1) or 1),
                    "fact_b_quote": str(ev_b.get("verbatim_quote", "")),
                    "fact_b_page": int(ev_b.get("page_number", 1) or 1),
                },
            }

    async def arbitrate_pair(self, fact_a: dict, fact_b: dict) -> dict:
        """Arbitrate two atomic facts and classify their epistemic relationship."""
        fact_a_dict = _fact_to_dict(fact_a)
        fact_b_dict = _fact_to_dict(fact_b)
        workspace_id = fact_a_dict.get("workspace_id") or fact_b_dict.get("workspace_id")

        # 1. Deterministic fast path (0 API calls)
        fast_res = self._deterministic_adjudication(fact_a_dict, fact_b_dict, workspace_id)
        if fast_res is not None:
            return fast_res

        # 2. LLM adjudication via Groq or Gemini
        if self.groq_api_key:
            return await self._arbitrate_groq(fact_a_dict, fact_b_dict, workspace_id)
        else:
            return await self._arbitrate_gemini(fact_a_dict, fact_b_dict, workspace_id)

    async def run_arbitration_for_workspace(
        self,
        workspace_id: uuid.UUID,
        new_document_id: Optional[uuid.UUID] = None,
        max_candidate_pairs: int = 50,
    ) -> list[dict]:
        """Run candidate blocking and pairwise arbitration for facts in a workspace.

        Args:
            workspace_id: The UUID of the workspace to arbitrate.
            new_document_id: Optional document UUID for incremental runs.
            max_candidate_pairs: Maximum number of candidate pairs to arbitrate in a single run.
        """
        if new_document_id is not None:
            facts_res = self.fact_repo.list_by_document(new_document_id)
        else:
            facts_res = self.fact_repo.list_by_workspace(workspace_id, skip=0, limit=10000)

        if inspect.isawaitable(facts_res):
            facts = await facts_res
        else:
            facts = facts_res

        if not facts:
            return []

        # Prioritize facts with numeric values and financial descriptors
        kpi_keywords = ("revenue", "ebitda", "profit", "loss", "pat", "pbt", "expense", "margin", "tonnage", "share", "parcel", "cash")
        prioritized = [f for f in facts if any(k in f.attribute.lower() for k in kpi_keywords)]
        other_facts = [f for f in facts if f not in prioritized]
        ordered_facts = prioritized + other_facts

        seen_pairs: set[frozenset[str]] = set()
        arbitration_results: list[dict] = []

        logger.info(
            "Starting cross-document arbitration for workspace %s: evaluating candidate pairs...",
            workspace_id,
        )

        for fact in ordered_facts:
            if len(arbitration_results) >= max_candidate_pairs:
                logger.info("Reached maximum candidate pairs limit (%d); wrapping up.", max_candidate_pairs)
                break

            fact_a_dict = _fact_to_dict(fact)
            fact_a_id = str(fact_a_dict.get("fact_id", ""))
            subject = str(fact_a_dict.get("subject", ""))
            attribute = str(fact_a_dict.get("attribute", ""))
            doc_id = str(fact_a_dict.get("document_id", ""))

            if not fact_a_id or not subject or not attribute:
                continue

            # Get anchor embedding
            embedding = await self.embedding_svc.embed_fact_anchor(subject, attribute)

            # Query cross-document candidates from ChromaDB
            candidates = self.vector_store.query_candidates(
                workspace_id=workspace_id,
                embedding=embedding,
                exclude_document_id=doc_id,
                top_k=5,
                threshold=0.84,
            )

            for candidate in candidates:
                if len(arbitration_results) >= max_candidate_pairs:
                    break

                cand_fact_id = str(candidate.get("fact_id", ""))
                if not cand_fact_id or cand_fact_id == fact_a_id:
                    continue

                pair_key = frozenset([fact_a_id, cand_fact_id])
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                fact_b = await self.fact_repo.get_by_id(cand_fact_id)
                if not fact_b:
                    continue

                fact_b_dict = _fact_to_dict(fact_b)
                result = await self.arbitrate_pair(fact_a_dict, fact_b_dict)
                arbitration_results.append(result)

                logger.info(
                    "Arbitrated pair %d/%d: %s vs %s -> %s (confidence: %.2f)",
                    len(arbitration_results),
                    max_candidate_pairs,
                    fact_a_id[:8],
                    cand_fact_id[:8],
                    result["relationship"],
                    result["confidence_score"],
                )

        logger.info(
            "Arbitration completed for workspace %s: %d pairs evaluated.",
            workspace_id,
            len(arbitration_results),
        )
        return arbitration_results

"""LLM-as-a-Judge Arbitration Engine Service for cross-document fact reconciliation."""

import asyncio
import inspect
import json
import logging
import re
from typing import Any, Optional, Union
import uuid

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


ARBITER_SYSTEM_PROMPT = (
    "You are an expert financial analyst and epistemic auditor.\n"
    "Your task is to compare two atomic facts extracted from documents and classify their relationship.\n\n"
    "Classification Rules:\n"
    "- CORROBORATED: The two facts assert the same subject, attribute, and value with matching context envelopes "
    "(or semantically equivalent phrasing and values).\n"
    "- CONTRADICTED: The two facts assert the same subject and attribute with matching context envelopes, "
    "but report conflicting irreconcilable values.\n"
    "- RECONCILED: The two facts have diverging values fully explained by differences in temporal_period, "
    "entity_scope, unit, or geography (e.g. Standalone vs Consolidated, Q3 vs FY, different units, distinct regions).\n"
    "- UNRELATED: The two facts refer to different subjects or attributes despite surface similarity.\n\n"
    "Output Requirements:\n"
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

    fact_a_quote: str = Field(..., description="Verbatim quote from Fact A")
    fact_a_page: int = Field(..., description="Page number where Fact A was cited")
    fact_b_quote: str = Field(..., description="Verbatim quote from Fact B")
    fact_b_page: int = Field(..., description="Page number where Fact B was cited")


class ArbitrationOutputSchema(BaseModel):
    """Schema for Gemini LLM-as-a-Judge structured response."""

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
        ...,
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


class ArbitrationService:
    """Service for cross-document fact arbitration and conflict reconciliation."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
        fact_repo: Any,
        client: Optional[genai.Client] = None,
        model: Optional[str] = None,
    ) -> None:
        """Initialize ArbitrationService.

        Args:
            embedding_service: Embedding service instance.
            vector_store: Vector store service instance.
            fact_repo: Fact repository instance.
            client: Optional google.genai Client override (e.g. for testing).
            model: Optional model identifier (defaults to gemini-3.8-flash).
        """
        if client is not None:
            self.client = client
        else:
            api_key = settings.GEMINI_API_KEY or "dummy-api-key"
            self.client = genai.Client(api_key=api_key)
        self.model = model or "gemini-3.8-flash"
        self.embedding_svc = embedding_service
        self.vector_store = vector_store
        self.fact_repo = fact_repo

    def _call_gemini_generate(
        self,
        prompt: str,
        config: types.GenerateContentConfig,
    ) -> Any:
        """Invoke Gemini models.generate_content synchronously."""
        try:
            return self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
        except TypeError as te:
            if "config" in str(te) or "generation_config" in str(te):
                return self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    generation_config=config,
                )
            raise

    async def _generate_content_async(
        self,
        prompt: str,
        config: types.GenerateContentConfig,
    ) -> Any:
        """Invoke Gemini generate_content asynchronously without blocking the event loop."""
        generate_fn = getattr(getattr(self.client, "models", None), "generate_content", None)
        if generate_fn is None:
            raise AttributeError("Client does not have models.generate_content")

        if inspect.iscoroutinefunction(generate_fn):
            return await generate_fn(model=self.model, contents=prompt, config=config)

        res = await asyncio.to_thread(self._call_gemini_generate, prompt, config)
        if inspect.isawaitable(res):
            return await res
        return res

    def _parse_arbitration_response(self, response: Any) -> dict[str, Any]:
        """Extract and validate JSON dictionary from Gemini response."""
        if isinstance(response, dict):
            validated = ArbitrationOutputSchema.model_validate(response)
            return validated.model_dump()

        parsed_attr = getattr(response, "parsed", None)
        if isinstance(parsed_attr, BaseModel):
            return parsed_attr.model_dump()
        if isinstance(parsed_attr, dict):
            validated = ArbitrationOutputSchema.model_validate(parsed_attr)
            return validated.model_dump()

        raw_text = getattr(response, "text", None)
        if isinstance(raw_text, str):
            cleaned = raw_text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned)

            data = json.loads(cleaned)
            if not isinstance(data, dict):
                raise ValueError(f"Expected dict response from Gemini, got {type(data)}")

            validated = ArbitrationOutputSchema.model_validate(data)
            return validated.model_dump()

        if isinstance(response, str):
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned)
            data = json.loads(cleaned)
            if isinstance(data, dict):
                validated = ArbitrationOutputSchema.model_validate(data)
                return validated.model_dump()

        raise ValueError(f"Unable to parse response of type {type(response)}")

    async def arbitrate_pair(self, fact_a: dict, fact_b: dict) -> dict:
        """Arbitrate two atomic facts and classify their epistemic relationship.

        Args:
            fact_a: First atomic fact dictionary or ORM object.
            fact_b: Second atomic fact dictionary or ORM object.

        Returns:
            Arbitration result dictionary containing:
            relationship, divergence_factor, confidence_score, reasoning_trace,
            evidence_comparison, fact_a_id, fact_b_id, arbitration_id, workspace_id.
        """
        fact_a_dict = _fact_to_dict(fact_a)
        fact_b_dict = _fact_to_dict(fact_b)

        fact_a_id = str(fact_a_dict.get("fact_id", ""))
        fact_b_id = str(fact_b_dict.get("fact_id", ""))
        workspace_id = fact_a_dict.get("workspace_id") or fact_b_dict.get("workspace_id")

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

        parsed_data: Optional[dict[str, Any]] = None
        last_error: Optional[Exception] = None

        for attempt in range(1, 3):
            try:
                response = await self._generate_content_async(prompt, config)
                parsed_data = self._parse_arbitration_response(response)
                break
            except Exception as exc:
                last_error = exc
                if attempt == 1:
                    logger.warning(
                        "Arbitration call attempt 1 failed for %s vs %s: %s. Retrying once...",
                        fact_a_id,
                        fact_b_id,
                        exc,
                    )
                else:
                    logger.error(
                        "Arbitration call failed for %s vs %s after retry: %s",
                        fact_a_id,
                        fact_b_id,
                        exc,
                    )

        ev_a = fact_a_dict.get("evidence") or {}
        ev_b = fact_b_dict.get("evidence") or {}

        if parsed_data is None:
            result = {
                "arbitration_id": str(uuid.uuid4()),
                "fact_a_id": fact_a_id,
                "fact_b_id": fact_b_id,
                "workspace_id": str(workspace_id) if workspace_id else None,
                "relationship": "UNRELATED",
                "divergence_factor": None,
                "confidence_score": 0.0,
                "reasoning_trace": (
                    f"Fallback adjudication: Arbitration failed due to malformed LLM response "
                    f"or API failure ({last_error}). Defaulted to UNRELATED."
                ),
                "evidence_comparison": {
                    "fact_a_quote": str(ev_a.get("verbatim_quote", "")),
                    "fact_a_page": int(ev_a.get("page_number", 1) or 1),
                    "fact_b_quote": str(ev_b.get("verbatim_quote", "")),
                    "fact_b_page": int(ev_b.get("page_number", 1) or 1),
                },
            }
        else:
            rel = str(parsed_data.get("relationship", "UNRELATED")).strip().upper()
            if rel not in {"CORROBORATED", "CONTRADICTED", "RECONCILED", "UNRELATED"}:
                rel = "UNRELATED"

            div_factor = parsed_data.get("divergence_factor")
            if rel != "RECONCILED":
                div_factor = None
            elif div_factor is not None:
                div_factor = str(div_factor)

            conf = float(parsed_data.get("confidence_score", 0.0))
            conf = max(0.0, min(1.0, conf))

            ev_comp = parsed_data.get("evidence_comparison") or {}
            fact_a_quote = str(ev_comp.get("fact_a_quote") or ev_a.get("verbatim_quote", ""))
            fact_a_page = int(ev_comp.get("fact_a_page") or ev_a.get("page_number", 1) or 1)
            fact_b_quote = str(ev_comp.get("fact_b_quote") or ev_b.get("verbatim_quote", ""))
            fact_b_page = int(ev_comp.get("fact_b_page") or ev_b.get("page_number", 1) or 1)

            result = {
                "arbitration_id": str(uuid.uuid4()),
                "fact_a_id": fact_a_id,
                "fact_b_id": fact_b_id,
                "workspace_id": str(workspace_id) if workspace_id else None,
                "relationship": rel,
                "divergence_factor": div_factor,
                "confidence_score": conf,
                "reasoning_trace": str(parsed_data.get("reasoning_trace", "")),
                "evidence_comparison": {
                    "fact_a_quote": fact_a_quote,
                    "fact_a_page": fact_a_page,
                    "fact_b_quote": fact_b_quote,
                    "fact_b_page": fact_b_page,
                },
            }

        logger.info(
            f"Arbitration result: {result['fact_a_id']} vs {result['fact_b_id']} -> {result['relationship']} (confidence: {result['confidence_score']})"
        )
        return result

    async def run_arbitration_for_workspace(
        self,
        workspace_id: uuid.UUID,
        new_document_id: Optional[uuid.UUID] = None,
    ) -> list[dict]:
        """Run candidate blocking and pairwise arbitration for facts in a workspace.

        Args:
            workspace_id: The UUID of the workspace to arbitrate.
            new_document_id: Optional document UUID. If provided, incremental arbitration is run
                only for facts belonging to this document against candidates from other documents.

        Returns:
            List of arbitration result dictionaries.
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

        seen_pairs: set[frozenset[str]] = set()
        arbitration_results: list[dict] = []

        for fact in facts:
            fact_a_dict = _fact_to_dict(fact)
            fact_a_id = str(fact_a_dict.get("fact_id", ""))
            subject = str(fact_a_dict.get("subject", ""))
            attribute = str(fact_a_dict.get("attribute", ""))
            doc_id = str(fact_a_dict.get("document_id", ""))

            if not fact_a_id or not subject or not attribute:
                continue

            # 1 & 2: Get anchor and embedding
            embedding = await self.embedding_svc.embed_fact_anchor(subject, attribute)

            # 3: Query candidates
            cand_res = self.vector_store.query_candidates(
                workspace_id=workspace_id,
                embedding=embedding,
                exclude_document_id=doc_id,
                top_k=20,
                threshold=0.82,
            )
            if inspect.isawaitable(cand_res):
                candidates = await cand_res
            else:
                candidates = cand_res

            logger.info(f"Found {len(candidates)} candidate pairs for fact {fact_a_id}")

            # 4 & 5: Deduplicate and arbitrate
            for candidate in candidates:
                cand_fact_id = str(candidate.get("fact_id", ""))
                if not cand_fact_id or cand_fact_id == fact_a_id:
                    continue

                pair_key = frozenset([fact_a_id, cand_fact_id])
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                fact_b_res = self.fact_repo.get_by_id(cand_fact_id)
                if inspect.isawaitable(fact_b_res):
                    fact_b = await fact_b_res
                else:
                    fact_b = fact_b_res

                if not fact_b:
                    logger.warning(
                        "Candidate fact %s not found in repository for arbitration",
                        cand_fact_id,
                    )
                    continue

                fact_b_dict = _fact_to_dict(fact_b)
                result = await self.arbitrate_pair(fact_a_dict, fact_b_dict)
                arbitration_results.append(result)

        return arbitration_results

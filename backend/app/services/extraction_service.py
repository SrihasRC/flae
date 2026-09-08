"""LLM-powered Atomic Fact Extraction Service using Gemini structured outputs."""

import asyncio
import inspect
import json
import logging
import re
from typing import Any, Optional
import uuid

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.gemini import GeminiClientPool
from app.services.pdf_parser import render_page_as_image

logger = logging.getLogger(__name__)


def validate_quote(quote: str, source_text: str) -> bool:
    """Validate that verbatim_quote is a substring of source_text after whitespace normalization.

    Args:
        quote: Candidate verbatim quote string to verify.
        source_text: Grounding source text against which the quote is matched.

    Returns:
        True if quote is found in source_text, False otherwise (logs Case 4 WARNING).
    """
    if not quote or not source_text:
        logger.warning(
            "Quote validation failure (Case 4): Empty quote or source text provided"
        )
        return False

    norm_quote = re.sub(r"\s+", " ", quote).strip()
    norm_source = re.sub(r"\s+", " ", source_text).strip()

    # Strip accidental surrounding quotation marks added by LLM
    if (norm_quote.startswith('"') and norm_quote.endswith('"')) or (
        norm_quote.startswith("'") and norm_quote.endswith("'")
    ):
        norm_quote = norm_quote[1:-1].strip()

    if norm_quote in norm_source:
        return True

    # Fallback check: normalize smart quotes and apostrophes
    cleaned_quote = (
        norm_quote.replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("‘", "'")
    )
    cleaned_source = (
        norm_source.replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("‘", "'")
    )
    if cleaned_quote in cleaned_source:
        return True

    logger.warning(
        "Quote validation failure (Case 4): Verbatim quote '%s' not found in source text",
        quote[:120],
    )
    return False


class ContextEnvelopeSchema(BaseModel):
    """Context qualification envelope for structured fact extraction."""

    temporal_period: Optional[str] = Field(
        default=None,
        description="Timeframe of the claim, e.g. 'FY2023-24' or 'Q3 FY24'",
    )
    period_type: Optional[str] = Field(
        default=None,
        description="'duration' for period spans or 'point_in_time' for snapshot dates",
    )
    entity_scope: Optional[str] = Field(
        default=None,
        description="Reporting perimeter, e.g. 'consolidated', 'standalone', 'subsidiary', 'cohort'",
    )
    geography: Optional[str] = Field(
        default=None, description="Geographic jurisdiction or region, e.g. 'India'"
    )
    accounting_methodology: Optional[str] = Field(
        default=None,
        description="Accounting or statistical reporting methodology, e.g. 'reported_ind_as', 'pro_forma', 'actual'",
    )
    additional_qualifiers: Optional[str] = Field(
        default=None,
        description="Other qualifiers like currency denomination, audit status, etc.",
    )


class EvidenceSchema(BaseModel):
    """Grounding evidence citation for structured fact extraction."""

    verbatim_quote: str = Field(
        ...,
        description="Exact textual excerpt from the source text grounding this fact",
    )
    page_number: int = Field(
        ..., description="Physical page number where the fact was cited"
    )
    section_title: Optional[str] = Field(
        default=None, description="Section or table header containing the fact"
    )


class ExtractedFact(BaseModel):
    """Schema representing an extracted atomic fact from Gemini structured output."""

    subject: str = Field(..., description="Entity or topic of the claim")
    attribute: str = Field(..., description="Property, metric, or relation measured")
    value_raw: str = Field(
        ..., description="Raw text value as reported in the document"
    )
    value_numeric: Optional[float] = Field(
        default=None, description="Normalized numeric value as a float, or null"
    )
    unit: Optional[str] = Field(
        default=None, description="Unit of measurement, or null"
    )
    context_envelope: ContextEnvelopeSchema = Field(
        default_factory=ContextEnvelopeSchema,
        description="Context qualification envelope",
    )
    evidence: EvidenceSchema = Field(
        ..., description="Verbatim citation grounding the fact"
    )


VISUAL_EXTRACTION_PROMPT = (
    "Extract ALL numerical facts, data labels, chart values, callout metrics, and table data visible in this page image.\n"
    "Return as a JSON array where each object strictly follows this schema:\n"
    "- subject: entity, company, or metric subject (string)\n"
    "- attribute: specific metric, dimension, or KPI name (string)\n"
    "- value_raw: exact visible value string (string, e.g. '₹1,250 Cr', '45.2%')\n"
    "- value_numeric: numeric float value if parseable, otherwise null\n"
    "- unit: unit of measurement (string, e.g. 'INR Cr', '%', 'USD'), otherwise null\n"
    "- context_envelope: object with temporal_period, period_type, entity_scope, geography, accounting_methodology, additional_qualifiers (all fields optional/null)\n"
    "- evidence: object with verbatim_quote (an exact visible phrase that includes both the label and value), page_number (the given page number), section_title (null)\n\n"
    "Return ONLY the valid JSON array."
)


class ExtractionService:
    """Service for extracting atomic facts from structured document blocks using Gemini."""

    DEFAULT_MODEL = "gemini-3.8-flash"
    BATCH_SIZE = 10
    # Seconds to sleep between successive Gemini calls (text batches and visual pages).
    # Helps avoid exhausting free-tier RPM quota across all 3 keys simultaneously.
    INTER_CALL_DELAY_SECONDS: float = 2.0

    SYSTEM_PROMPT = (
        "You are an expert financial data analyst and information extraction system.\n"
        "Your mission is to extract atomic facts explicitly stated in the provided text blocks.\n\n"
        "Strict Guardrails:\n"
        "1. Extract ONLY facts that are explicitly and directly stated in the text.\n"
        "2. Require VERBATIM quotes: Every fact must have an exact, verbatim quote in evidence.verbatim_quote from the source text. The quote must include the reported value and enough nearby label/context to identify one physical PDF page.\n"
        "3. Do NOT infer, extrapolate, assume, or hallucinate values, numbers, dates, or scopes.\n"
        "4. For numeric facts, extract the raw representation (value_raw) as well as the normalized numeric float value (value_numeric) and unit where available.\n"
        "5. Accurately populate the context_envelope:\n"
        "   - temporal_period: Explicit period or date (e.g., 'FY2023-24', 'Q3 FY24', 'As of March 31, 2024').\n"
        "   - period_type: Either 'duration' (for time spans/periods) or 'point_in_time' (for snapshot dates/balance sheet dates).\n"
        "   - entity_scope: Reporting perimeter (e.g., 'consolidated', 'standalone', 'subsidiary', 'cohort').\n"
        "   - geography: Geographic jurisdiction or region (e.g., 'India', 'Global').\n"
        "   - accounting_methodology: Standard used (e.g., 'reported_ind_as', 'pro_forma', 'actual', 'budget_estimate').\n"
        "   - additional_qualifiers: Any extra qualifiers such as audited status, currency denomination, etc.\n"
        "6. Return the extracted facts as a JSON array matching the requested schema."
    )

    def __init__(
        self,
        client: Optional[genai.Client] = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        """Initialize the extraction service with a Gemini client."""
        if client is not None:
            self._client_pool = GeminiClientPool(client=client)
        else:
            self._client_pool = GeminiClientPool()
        self.client = self._client_pool.client
        self.model = model

    def _build_batch_prompt(self, batch: list) -> tuple[str, str]:
        """Build the batch prompt and concatenated source text for quote verification."""
        block_descriptions: list[str] = []
        source_texts: list[str] = []

        for idx, block in enumerate(batch, start=1):
            if isinstance(block, dict):
                page_num = block.get("page_number", 1)
                block_type = block.get("block_type", "text")
                content = block.get("content", "")
                raw_markdown = block.get("raw_markdown", "")
            else:
                page_num = getattr(block, "page_number", 1)
                block_type = getattr(block, "block_type", "text")
                content = getattr(block, "content", "")
                raw_markdown = getattr(block, "raw_markdown", "")

            body = content if content else raw_markdown
            block_descriptions.append(
                f"--- Block {idx} (Page {page_num}, Type: {block_type}) ---\n{body}"
            )

            if content:
                source_texts.append(str(content))
            if raw_markdown:
                source_texts.append(str(raw_markdown))

        prompt = (
            "Extract all atomic facts explicitly stated in the following document blocks. "
            "Each fact must include an exact verbatim quote from the text.\n\n"
            + "\n\n".join(block_descriptions)
        )
        combined_source = " ".join(source_texts)
        return prompt, combined_source

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    def _call_gemini_generate(
        self,
        prompt: str,
        config: types.GenerateContentConfig,
    ) -> Any:
        """Invoke Gemini models.generate_content with retry logic."""
        try:
            return self._client_pool.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
        except TypeError as te:
            if "config" in str(te) or "generation_config" in str(te):
                return self._client_pool.generate_content(
                    model=self.model,
                    contents=prompt,
                    generation_config=config,
                )
            raise

    async def extract_facts_from_image(
        self,
        image_bytes: bytes,
        page_number: int,
        document_id: Any,
        workspace_id: Any,
        source_text: str,
    ) -> list[dict]:
        """Extract facts from a page image using Gemini multimodal API."""
        if not image_bytes:
            return []

        doc_id_str = str(document_id)
        ws_id_str = str(workspace_id)

        def _call_visual() -> Any:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
            text_part = types.Part.from_text(text=VISUAL_EXTRACTION_PROMPT)
            return self._client_pool.generate_content(
                model=self.model,
                contents=[image_part, text_part],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )

        try:
            response = await asyncio.to_thread(_call_visual)
            if inspect.isawaitable(response):
                response = await response

            raw_text = getattr(response, "text", None)
            if raw_text is None:
                if isinstance(response, (dict, list)):
                    parsed_json = response
                else:
                    raw_text = str(response)
                    parsed_json = None
            else:
                parsed_json = None

            if parsed_json is None:
                cleaned = raw_text.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
                    cleaned = re.sub(r"\n?```$", "", cleaned)
                parsed_json = json.loads(cleaned)

            if isinstance(parsed_json, dict):
                if "facts" in parsed_json and isinstance(parsed_json["facts"], list):
                    raw_facts = parsed_json["facts"]
                else:
                    raw_facts = [parsed_json]
            elif isinstance(parsed_json, list):
                raw_facts = parsed_json
            else:
                raw_facts = []

            facts: list[dict] = []
            for item in raw_facts:
                if not isinstance(item, dict):
                    continue

                context_env = item.get("context_envelope") or {}
                if not isinstance(context_env, dict):
                    context_env = {}

                evidence = item.get("evidence") or {}
                if not isinstance(evidence, dict):
                    evidence = {}

                val_numeric = item.get("value_numeric")
                if val_numeric is not None:
                    try:
                        val_numeric = float(val_numeric)
                    except (ValueError, TypeError):
                        val_numeric = None

                quote = str(evidence.get("verbatim_quote", ""))
                if not validate_quote(quote, source_text):
                    continue

                try:
                    validated = ExtractedFact.model_validate(item)
                except Exception as exc:
                    logger.warning(
                        "Visual extraction validation failure (Case 4) on page %d: %s",
                        page_number,
                        exc,
                    )
                    continue

                if not validated.subject.strip() or not validated.attribute.strip() or not validated.value_raw.strip():
                    logger.warning("Visual extraction returned an incomplete fact (Case 4) on page %d", page_number)
                    continue

                fact_dict: dict[str, Any] = {
                    "subject": validated.subject,
                    "attribute": validated.attribute,
                    "value_raw": validated.value_raw,
                    "value_numeric": val_numeric,
                    "unit": item.get("unit"),
                    "context_envelope": {
                        "temporal_period": context_env.get("temporal_period"),
                        "period_type": context_env.get("period_type"),
                        "entity_scope": context_env.get("entity_scope"),
                        "geography": context_env.get("geography"),
                        "accounting_methodology": context_env.get(
                            "accounting_methodology"
                        ),
                        "additional_qualifiers": context_env.get(
                            "additional_qualifiers"
                        ),
                    },
                    "evidence": {
                        "verbatim_quote": str(quote),
                        "page_number": page_number,
                        "section_title": None,
                    },
                    "document_id": doc_id_str,
                    "workspace_id": ws_id_str,
                }
                if "fact_id" in item and item["fact_id"]:
                    fact_dict["fact_id"] = str(item["fact_id"])

                facts.append(fact_dict)

            logger.info(
                "Visual fact extraction complete for page %d (%d facts)",
                page_number,
                len(facts),
            )
            return facts

        except Exception as exc:
            logger.warning(
                "Visual fact extraction failed for page %d: %s",
                page_number,
                exc,
            )
            return []

    @staticmethod
    def _source_text_by_page(blocks: list) -> dict[int, str]:
        """Return the extractable source text for each physical PDF page."""
        source_by_page: dict[int, list[str]] = {}
        for block in blocks:
            page_number = (
                block.get("page_number", 1)
                if isinstance(block, dict)
                else getattr(block, "page_number", 1)
            )
            content = (
                block.get("content", "")
                if isinstance(block, dict)
                else getattr(block, "content", "")
            )
            raw_markdown = (
                block.get("raw_markdown", "")
                if isinstance(block, dict)
                else getattr(block, "raw_markdown", "")
            )
            source_by_page.setdefault(int(page_number), []).extend(
                str(text) for text in (content, raw_markdown) if text
            )
        return {page: "\n".join(parts) for page, parts in source_by_page.items()}

    @staticmethod
    def _find_grounding_page(quote: str, source_by_page: dict[int, str]) -> int | None:
        """Find the one physical PDF page that contains a quoted source passage."""
        matching_pages = [
            page for page, source_text in source_by_page.items() if validate_quote(quote, source_text)
        ]
        if len(matching_pages) != 1:
            logger.warning(
                "Quote provenance failure (Case 4): quote matched %d pages; dropping fact",
                len(matching_pages),
            )
            return None
        return matching_pages[0]

    async def extract_facts(
        self,
        blocks: list | tuple,
        document_id: uuid.UUID | str,
        workspace_id: uuid.UUID | str,
        visual_pages: list[int] | None = None,
        file_bytes: bytes | None = None,
    ) -> list[dict]:
        """Extract and validate atomic facts from document blocks or page images.

        Args:
            blocks: List of parsed blocks or tuple (blocks, visual_pages).
            document_id: Source document UUID or string.
            workspace_id: Target workspace UUID or string.
            visual_pages: Optional list of 1-indexed page numbers flagged for vision extraction.
            file_bytes: Optional raw PDF file bytes for rendering page images.

        Returns:
            List of validated atomic fact dictionaries ready for DB insertion.
        """
        # Handle tuple return from parse_pdf if passed directly as blocks
        if isinstance(blocks, tuple) and len(blocks) == 2:
            if visual_pages is None and isinstance(blocks[1], list):
                visual_pages = blocks[1]
            blocks = blocks[0]

        doc_id_str = str(document_id)
        ws_id_str = str(workspace_id)
        all_validated_facts: list[dict] = []
        source_by_page = self._source_text_by_page(list(blocks or []))

        visual_set = set(visual_pages) if visual_pages else set()

        # Visual extraction path: for pages in visual_pages, call extract_facts_from_image
        if visual_pages:
            for page_num in visual_pages:
                try:
                    img_bytes = render_page_as_image(file_bytes=file_bytes, page_number=page_num)
                    if img_bytes:
                        visual_facts = await self.extract_facts_from_image(
                            image_bytes=img_bytes,
                            page_number=page_num,
                            document_id=doc_id_str,
                            workspace_id=ws_id_str,
                            source_text=source_by_page.get(page_num, ""),
                        )
                        all_validated_facts.extend(visual_facts)
                except Exception as exc:
                    logger.warning(
                        "Vision extraction fallback failed for page %d: %s",
                        page_num,
                        exc,
                    )
                # Pace calls: avoid hitting all keys simultaneously across visual pages
                if visual_pages and page_num != visual_pages[-1]:
                    await asyncio.sleep(self.INTER_CALL_DELAY_SECONDS)

        # Text extraction path: skip blocks on visual pages
        text_blocks = [
            b
            for b in (blocks or [])
            if (
                getattr(b, "page_number", None)
                or (b.get("page_number") if isinstance(b, dict) else None)
            )
            not in visual_set
        ]

        if not text_blocks:
            logger.info("Fact extraction complete (%d facts)", len(all_validated_facts))
            return all_validated_facts

        # Group blocks into batches of up to 10 blocks
        batches = [
            text_blocks[i : i + self.BATCH_SIZE]
            for i in range(0, len(text_blocks), self.BATCH_SIZE)
        ]

        for batch_idx, batch in enumerate(batches, start=1):
            prompt, batch_source_text = self._build_batch_prompt(batch)
            if not batch_source_text.strip():
                continue

            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[ExtractedFact],
                system_instruction=self.SYSTEM_PROMPT,
            )

            try:
                response = await asyncio.to_thread(self._call_gemini_generate, prompt, config)
                if inspect.isawaitable(response):
                    response = await response
            except Exception as exc:
                logger.error(
                    "Error calling Gemini API for batch %d: %s",
                    batch_idx,
                    exc,
                )
                # Still pace even on error to avoid rapid-fire retries from caller
                if batch_idx < len(batches):
                    await asyncio.sleep(self.INTER_CALL_DELAY_SECONDS)
                continue

            # Extract raw response text
            raw_text = getattr(response, "text", None)
            if raw_text is None:
                if isinstance(response, (dict, list)):
                    parsed_json = response
                else:
                    raw_text = str(response)
                    parsed_json = None
            else:
                parsed_json = None

            # Handle JSON parsing gracefully
            if parsed_json is None:
                try:
                    parsed_json = json.loads(raw_text)
                except json.JSONDecodeError as err:
                    cleaned = raw_text.strip()
                    if cleaned.startswith("```"):
                        cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
                        cleaned = re.sub(r"\n?```$", "", cleaned)
                        try:
                            parsed_json = json.loads(cleaned)
                        except json.JSONDecodeError:
                            logger.error(
                                "Failed to parse JSON from Gemini response for batch %d: %s",
                                batch_idx,
                                err,
                            )
                            continue
                    else:
                        logger.error(
                            "Failed to parse JSON from Gemini response for batch %d: %s",
                            batch_idx,
                            err,
                        )
                        continue

            # Normalize parsed JSON into a list of candidate fact dictionaries
            if isinstance(parsed_json, list):
                raw_facts = parsed_json
            elif isinstance(parsed_json, dict):
                if "facts" in parsed_json and isinstance(parsed_json["facts"], list):
                    raw_facts = parsed_json["facts"]
                else:
                    raw_facts = [parsed_json]
            else:
                logger.error(
                    "Unexpected JSON structure for batch %d: expected list or dict, got %s",
                    batch_idx,
                    type(parsed_json),
                )
                continue

            # Validate each fact's verbatim quote against the batch source text
            for item in raw_facts:
                if not isinstance(item, dict):
                    continue

                evidence = item.get("evidence") or {}
                if not isinstance(evidence, dict):
                    evidence = {}
                quote = str(evidence.get("verbatim_quote", ""))

                grounding_page = self._find_grounding_page(quote, source_by_page)
                if grounding_page is None:
                    continue

                try:
                    validated = ExtractedFact.model_validate(item)
                except Exception as exc:
                    logger.warning("Extraction validation failure (Case 4): %s", exc)
                    continue
                if not validated.subject.strip() or not validated.attribute.strip() or not validated.value_raw.strip():
                    logger.warning("Extraction returned an incomplete fact (Case 4)")
                    continue

                context_env = item.get("context_envelope") or {}
                if not isinstance(context_env, dict):
                    context_env = {}

                val_numeric = item.get("value_numeric")
                if val_numeric is not None:
                    try:
                        val_numeric = float(val_numeric)
                    except (ValueError, TypeError):
                        val_numeric = None

                fact_dict: dict[str, Any] = {
                    "subject": validated.subject,
                    "attribute": validated.attribute,
                    "value_raw": validated.value_raw,
                    "value_numeric": val_numeric,
                    "unit": item.get("unit"),
                    "context_envelope": {
                        "temporal_period": context_env.get("temporal_period"),
                        "period_type": context_env.get("period_type"),
                        "entity_scope": context_env.get("entity_scope"),
                        "geography": context_env.get("geography"),
                        "accounting_methodology": context_env.get(
                            "accounting_methodology"
                        ),
                        "additional_qualifiers": context_env.get(
                            "additional_qualifiers"
                        ),
                    },
                    "evidence": {
                        "verbatim_quote": quote,
                        "page_number": grounding_page,
                        "section_title": evidence.get("section_title"),
                    },
                    "document_id": doc_id_str,
                    "workspace_id": ws_id_str,
                }
                if "fact_id" in item and item["fact_id"]:
                    fact_dict["fact_id"] = str(item["fact_id"])

                all_validated_facts.append(fact_dict)

            # Pace calls: give Gemini API time between batches to avoid RPM throttling
            if batch_idx < len(batches):
                await asyncio.sleep(self.INTER_CALL_DELAY_SECONDS)

        logger.info("Fact extraction complete (%d facts)", len(all_validated_facts))
        return all_validated_facts

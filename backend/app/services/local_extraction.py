"""Rule-based atomic fact extractor that runs entirely locally — no LLM/API calls.

Extracts facts directly from the structured ParsedBlocks produced by pdf_parser:
  - callout  → numeric KPI stat
  - table    → one fact per data cell (column-header × row-label × value)
  - text     → sentences that contain a clearly bounded numeric measurement
  - footnote → bound to its parent table, not extracted separately

All quote grounding uses the block's raw_markdown / content directly, so
verbatim_quote always matches the source text.
"""

import logging
import re
import uuid
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Numeric / unit patterns
# ---------------------------------------------------------------------------
_CURRENCY_RE = re.compile(r"[₹$€£]|Rs\.?|INR|USD", re.IGNORECASE)
_SCALE_RE = re.compile(r"\b(Mn|Bn|Cr|Crore|Crores|Lakh|Lakhs|Tons?|Tonnes?|Million|Billion|bps)\b", re.IGNORECASE)
_PCT_RE = re.compile(r"\d+\.?\d*\s*%")
_NUMBER_RE = re.compile(r"[-+]?[\d,]+\.?\d*")
_TEMPORAL_RE = re.compile(
    r"\b(Q[1-4]\s*FY\s*\d{2,4}|FY\s*\d{2,4}|H[12]\s*FY\s*\d{2,4}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)['\s]\d{2,4}|"
    r"\d{4}-\d{2,4}|As\s+of\s+\w+\s+\d+,?\s*\d{4})\b",
    re.IGNORECASE,
)
# A "significant" numeric: has currency, scale unit, or percentage
_SIGNIFICANT_RE = re.compile(
    r"(?:[₹$€£]|Rs\.?|INR|USD|\bMn\b|\bBn\b|\bCr\b|\bLakh\b|\bTon|\b\d+\.?\d*\s*%)",
    re.IGNORECASE,
)


def _parse_numeric(text: str) -> tuple[Optional[float], Optional[str]]:
    """Return (value_numeric, unit) from a raw value string."""
    cleaned = text.replace(",", "")
    m = _NUMBER_RE.search(cleaned)
    value_numeric = float(m.group()) if m else None

    unit_parts: list[str] = []
    cm = _CURRENCY_RE.search(text)
    if cm:
        unit_parts.append(cm.group().strip())
    sm = _SCALE_RE.search(text)
    if sm:
        unit_parts.append(sm.group().strip())
    if "%" in text:
        unit_parts.append("%")

    unit = " ".join(unit_parts) if unit_parts else None
    return value_numeric, unit


def _temporal(text: str) -> Optional[str]:
    m = _TEMPORAL_RE.search(text)
    return m.group().strip() if m else None


def _subject_from_filename(filename: str) -> str:
    """Best-effort company/entity name from a document filename."""
    stem = Path(filename).stem
    # Strip leading numeric prefix like "03-"
    stem = re.sub(r"^\d+[-_]", "", stem)
    parts = re.split(r"[-_]", stem)
    # Capitalise and drop generic words
    skip = {"q1", "q2", "q3", "q4", "fy", "fy24", "fy23", "fy22",
            "earnings", "presentation", "report", "annual", "results",
            "investor", "update", "deck", "slides"}
    name_parts = [p.capitalize() for p in parts if p.lower() not in skip and len(p) > 1]
    return " ".join(name_parts[:3]) if name_parts else stem.capitalize()


# ---------------------------------------------------------------------------
# Per-block extractors
# ---------------------------------------------------------------------------

def _facts_from_callout(block: Any, subject: str, document_id: str, workspace_id: str) -> list[dict]:
    """A callout block IS a single numeric fact."""
    text = (getattr(block, "content", None) or block.get("content", "")) if isinstance(block, dict) else getattr(block, "content", "")
    raw_md = (getattr(block, "raw_markdown", None) or block.get("raw_markdown", "")) if isinstance(block, dict) else getattr(block, "raw_markdown", "")
    page_num = (block.get("page_number", 1) if isinstance(block, dict) else getattr(block, "page_number", 1))
    quote = raw_md or text
    if not text.strip():
        return []

    value_numeric, unit = _parse_numeric(text)
    temporal = _temporal(text)
    return [{
        "subject": subject,
        "attribute": text.strip(),
        "value_raw": text.strip(),
        "value_numeric": value_numeric,
        "unit": unit,
        "context_envelope": {
            "temporal_period": temporal,
            "period_type": "duration" if temporal else None,
            "entity_scope": None,
            "geography": None,
            "accounting_methodology": None,
            "additional_qualifiers": None,
        },
        "evidence": {
            "verbatim_quote": quote.strip(),
            "page_number": page_num,
            "section_title": None,
        },
        "document_id": document_id,
        "workspace_id": workspace_id,
    }]


def _facts_from_table(block: Any, subject: str, document_id: str, workspace_id: str) -> list[dict]:
    """Parse a markdown table block and emit one fact per data cell that has a numeric value."""
    raw_md = (block.get("raw_markdown", "") if isinstance(block, dict) else getattr(block, "raw_markdown", ""))
    page_num = (block.get("page_number", 1) if isinstance(block, dict) else getattr(block, "page_number", 1))
    if not raw_md:
        return []

    lines = [l.strip() for l in raw_md.strip().splitlines() if l.strip()]
    if len(lines) < 3:
        return []

    # Parse header row
    header_cells = [h.strip() for h in lines[0].split("|")]
    header_cells = [h for h in header_cells if h]  # drop empty strings from leading/trailing |

    # lines[1] is separator — skip
    facts: list[dict] = []
    for data_line in lines[2:]:
        cells = [c.strip() for c in data_line.split("|")]
        cells = [c for c in cells if c or c == ""]  # preserve structure
        # Rebuild: split gives empty strings for leading/trailing |
        non_empty_cells = [c for c in data_line.split("|")]
        # Drop first and last if empty (artifact of | col | syntax)
        if non_empty_cells and non_empty_cells[0].strip() == "":
            non_empty_cells = non_empty_cells[1:]
        if non_empty_cells and non_empty_cells[-1].strip() == "":
            non_empty_cells = non_empty_cells[:-1]
        cells = [c.strip() for c in non_empty_cells]

        if not cells:
            continue
        row_label = cells[0]

        for col_idx, cell_val in enumerate(cells[1:], start=1):
            if not cell_val or not _SIGNIFICANT_RE.search(cell_val):
                # Only extract cells with a meaningful numeric value
                if not _NUMBER_RE.search(cell_val):
                    continue
                # Has a number but no currency/scale/pct — skip unless it looks like a real metric
                raw_num = cell_val.replace(",", "").strip()
                try:
                    fval = float(raw_num)
                except ValueError:
                    continue
                if abs(fval) < 0.01:
                    continue

            col_header = header_cells[col_idx] if col_idx < len(header_cells) else f"Col{col_idx}"
            temporal = _temporal(col_header) or _temporal(row_label)

            # Attribute = "row_label — col_header" or just col_header if row_label is empty/generic
            attribute_parts = []
            if row_label and row_label not in {"-", "—", "–", ""}:
                attribute_parts.append(row_label)
            if col_header and col_header not in {"-", "—", "–", ""}:
                attribute_parts.append(col_header)
            attribute = " — ".join(attribute_parts) if attribute_parts else cell_val

            value_numeric, unit = _parse_numeric(cell_val)
            # Verbatim quote: use the full table row for grounding
            verbatim_quote = data_line.strip()

            facts.append({
                "subject": subject,
                "attribute": attribute,
                "value_raw": cell_val,
                "value_numeric": value_numeric,
                "unit": unit,
                "context_envelope": {
                    "temporal_period": temporal,
                    "period_type": "duration" if temporal else None,
                    "entity_scope": None,
                    "geography": None,
                    "accounting_methodology": None,
                    "additional_qualifiers": None,
                },
                "evidence": {
                    "verbatim_quote": verbatim_quote,
                    "page_number": page_num,
                    "section_title": None,
                },
                "document_id": document_id,
                "workspace_id": workspace_id,
            })
    return facts


def _facts_from_text(block: Any, subject: str, document_id: str, workspace_id: str) -> list[dict]:
    """Extract sentences from a text block that contain a clearly bounded numeric measurement."""
    raw_md = (block.get("raw_markdown", "") if isinstance(block, dict) else getattr(block, "raw_markdown", ""))
    content = (block.get("content", "") if isinstance(block, dict) else getattr(block, "content", ""))
    page_num = (block.get("page_number", 1) if isinstance(block, dict) else getattr(block, "page_number", 1))
    text = raw_md or content
    if not text.strip():
        return []

    # Split into sentences on . ; \n bullet points
    sentences = re.split(r"(?<=[.;])\s+|\n+|(?<=\d)\s*[-–—]\s*(?=[A-Z])", text)
    facts: list[dict] = []
    seen: set[str] = set()

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 8 or len(sent) > 300:
            continue
        if not _SIGNIFICANT_RE.search(sent):
            continue
        if sent in seen:
            continue
        seen.add(sent)

        # Try to split "Label: value" or "Label — value"
        split_m = re.split(r"\s*[:—–]\s+", sent, maxsplit=1)
        if len(split_m) == 2:
            label, value_part = split_m
            attribute = label.strip()
            value_raw = value_part.strip()
        else:
            # Use the whole sentence as both attribute and value
            attribute = sent
            value_raw = sent

        value_numeric, unit = _parse_numeric(value_raw)
        temporal = _temporal(sent)

        facts.append({
            "subject": subject,
            "attribute": attribute,
            "value_raw": value_raw,
            "value_numeric": value_numeric,
            "unit": unit,
            "context_envelope": {
                "temporal_period": temporal,
                "period_type": "duration" if temporal else None,
                "entity_scope": None,
                "geography": None,
                "accounting_methodology": None,
                "additional_qualifiers": None,
            },
            "evidence": {
                "verbatim_quote": sent,
                "page_number": page_num,
                "section_title": None,
            },
            "document_id": document_id,
            "workspace_id": workspace_id,
        })
    return facts


# ---------------------------------------------------------------------------
# Main service
# ---------------------------------------------------------------------------

class LocalExtractionService:
    """Offline, rule-based fact extractor. Zero API calls, instant execution."""

    async def extract_facts(
        self,
        blocks: list | tuple,
        document_id: Any,
        workspace_id: Any,
        visual_pages: Optional[list[int]] = None,
        file_bytes: Optional[bytes] = None,
        filename: str = "",
    ) -> list[dict]:
        """Extract atomic facts from parsed PDF blocks without any LLM call."""
        # Unpack tuple form (blocks, visual_pages) for compatibility
        if isinstance(blocks, tuple) and len(blocks) == 2:
            blocks = blocks[0]

        doc_id_str = str(document_id)
        ws_id_str = str(workspace_id)
        subject = _subject_from_filename(filename) if filename else "Document"

        all_facts: list[dict] = []
        seen_facts: set[tuple[str, str, int]] = set()

        for block in (blocks or []):
            b_type = (block.get("block_type") if isinstance(block, dict) else getattr(block, "block_type", "text"))

            if b_type == "callout":
                new_facts = _facts_from_callout(block, subject, doc_id_str, ws_id_str)
            elif b_type == "table":
                new_facts = _facts_from_table(block, subject, doc_id_str, ws_id_str)
            elif b_type == "text":
                new_facts = _facts_from_text(block, subject, doc_id_str, ws_id_str)
            else:
                # footnotes are already bound to their table — skip
                continue

            # Deduplicate by (attribute, value_raw, page_number)
            for fact in new_facts:
                attr = fact.get("attribute", "")
                val = fact.get("value_raw", "")
                pg = fact.get("evidence", {}).get("page_number", 0)
                fact_key = (attr, val, pg)
                if fact_key not in seen_facts:
                    seen_facts.add(fact_key)
                    all_facts.append(fact)

        logger.info(
            "Local fact extraction complete: %d facts from %d blocks",
            len(all_facts),
            len(list(blocks or [])),
        )
        return all_facts

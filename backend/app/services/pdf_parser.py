"""Layout-aware PDF parsing and document structure extraction service.

Converts raw PDF bytes into structured, LLM-ready ParsedBlocks preserving
reading order, layout, table boundaries, stat callouts, and footnotes.
"""

from dataclasses import dataclass
import io
import logging
import re
from typing import Any, Literal

import pdfplumber
import pymupdf as fitz
import pymupdf4llm

logger = logging.getLogger(__name__)


@dataclass
class ParsedBlock:
    """Represents a structured block extracted from a PDF document."""

    page_number: int
    block_type: Literal["text", "table", "footnote", "callout"]
    content: str  # clean text content
    raw_markdown: str  # original markdown representation


# Regex for detecting footnote prefixes
FOOTNOTE_PREFIX_REGEX = re.compile(
    r"^(\s*)([†‡§#]+|\([0-9a-zA-Z]{1,2}\)|\[[0-9a-zA-Z]{1,2}\]|[0-9]{1,2}[\.\/](?=\s)|<sup>[†‡#0-9a-zA-Z]+</sup>|notes?:|sources?:)",
    re.IGNORECASE,
)

# Currency symbols and financial scale units for callouts
CURRENCY_REGEX = re.compile(r"(₹|\$|€|£|Rs\.?|INR|USD)", re.IGNORECASE)
SCALE_UNIT_REGEX = re.compile(
    r"\b(Mn|Bn|Cr|Crore|Crores|Lakh|Lakhs|Tons?|Tonnes?|Million|Billion|Trillion|bps)\b",
    re.IGNORECASE,
)


def extract_pdf_metadata(file_bytes: bytes) -> dict[str, Any]:
    """Extract basic metadata from a PDF file in bytes.

    Returns:
        dict with page_count (int), title (str), and author (str).
    """
    if not file_bytes:
        return {"page_count": 0, "title": "", "author": ""}

    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        metadata = doc.metadata or {}
        title = str(metadata.get("title") or "").strip()
        author = str(metadata.get("author") or "").strip()
        return {
            "page_count": int(doc.page_count),
            "title": title,
            "author": author,
        }


# Alias for compatibility with PLAN.md naming
extract_text_metadata = extract_pdf_metadata


def _clean_markdown_to_text(md: str) -> str:
    """Convert raw markdown to clean, readable plain text while preserving structure."""
    # Replace HTML breaks with space
    text = re.sub(r"<br\s*/?>", " ", md, flags=re.IGNORECASE)
    # Strip remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Convert markdown links [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    lines: list[str] = []
    for line in text.splitlines():
        prefix = ""
        bullet_match = re.match(r"^(\s*[\*\-\+]\s+)(.*)$", line)
        if bullet_match:
            prefix = bullet_match.group(1)
            line = bullet_match.group(2)
        # Strip header markers (#, ##, etc.)
        line = re.sub(r"^#+\s*", "", line)
        # Strip bold/italics
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        line = re.sub(r"__([^_]+)__", r"\1", line)
        line = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", line)
        line = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", line)
        # Strip backticks
        line = re.sub(r"`([^`]+)`", r"\1", line)
        lines.append(prefix + line)

    clean = "\n".join(lines).strip()
    cleaned_lines = [re.sub(r"[ \t]+", " ", l).strip() for l in clean.splitlines()]
    return "\n".join(l for l in cleaned_lines if l)


def _is_markdown_table(text: str) -> bool:
    """Check if a text block represents a markdown table."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if len(lines) < 2:
        return False
    pipe_lines = sum(1 for line in lines if line.startswith("|") and line.endswith("|"))
    if pipe_lines >= 2:
        for line in lines[1:4]:
            if re.match(r"^\|(\s*:?-+:?\s*\|)+$", line):
                return True
    return False


def _strip_outer_markdown_emphasis(text: str) -> str:
    """Remove leading Markdown emphasis before classifying a content block."""
    clean = text.strip()
    while clean.startswith(("**", "__")):
        clean = clean[2:].lstrip()
    if clean.startswith("_("):
        clean = clean[1:]
    return clean


def _is_footnote_block(text: str, chunk_idx: int, total_chunks: int, prev_block_type: str = "") -> bool:
    """Check if a block represents a footnote or citation."""
    clean = _strip_outer_markdown_emphasis(text)
    if clean.startswith("#"):
        return False
    match = FOOTNOTE_PREFIX_REGEX.match(clean)
    if not match:
        return False
    marker = match.group(2).lower()
    # Explicit footnote markers or Note/Source labels are footnotes anywhere
    if any(s in marker for s in ["*", "†", "‡", "§"]) or marker.startswith("note") or marker.startswith("source"):
        return True
    # Numbered patterns (1., 2., (1), 1/) are footnotes if in bottom half of page or following a table
    is_near_bottom = (total_chunks > 1 and chunk_idx >= max(1, total_chunks // 2))
    if is_near_bottom or prev_block_type == "table":
        return True
    return False


def _is_callout_block(text: str) -> bool:
    """Check if a block represents a visual stat callout (isolated short numeric-heavy block)."""
    clean = _clean_markdown_to_text(text).strip()
    words = clean.split()
    if not words or len(words) >= 20:
        return False

    # Exclude single page numbers or fiscal year labels
    if len(words) == 1:
        w = words[0].strip()
        if w.isdigit() and len(w) <= 4:
            return False
        if re.match(r"^FY\d{2,4}$", w, re.IGNORECASE):
            return False

    if not any(c.isdigit() for c in clean):
        return False

    has_currency = bool(CURRENCY_REGEX.search(clean))
    has_scale = bool(SCALE_UNIT_REGEX.search(clean))
    has_pct = "%" in clean

    digits_count = sum(1 for c in clean if c.isdigit())
    letters_count = sum(1 for c in clean if c.isalpha())

    # Numeric heavy if currency/unit/percentage present, or high digit ratio
    if (has_currency or has_scale or has_pct) and digits_count >= 1:
        return True
    if digits_count >= 3 and digits_count >= letters_count * 0.4:
        return True

    return False


def _format_plumber_table(table_rows: list[list[str | None]]) -> tuple[str, str]:
    """Convert a 2D pdfplumber table into clean text and raw markdown."""
    cleaned_rows: list[list[str]] = []
    for row in table_rows:
        cleaned_row = [re.sub(r"\s+", " ", cell).strip() if cell else "" for cell in row]
        if any(cleaned_row):
            cleaned_rows.append(cleaned_row)

    if not cleaned_rows:
        return "", ""

    max_cols = max(len(row) for row in cleaned_rows)
    if max_cols < 2 or len(cleaned_rows) < 2:
        return "", ""

    norm_rows = [row + [""] * (max_cols - len(row)) for row in cleaned_rows]
    header = norm_rows[0]
    separator = ["---"] * max_cols
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(separator) + " |"]
    for row in norm_rows[1:]:
        lines.append("| " + " | ".join(row) + " |")

    raw_md = "\n".join(lines)
    content = _clean_markdown_to_text(raw_md)
    return content, raw_md


def _is_table_already_captured(table_rows: list[list[str | None]], existing_blocks: list[ParsedBlock]) -> bool:
    """Check if a pdfplumber table is already captured by an existing table block on the page."""
    cells = [
        re.sub(r"\s+", " ", cell).strip()
        for row in table_rows
        for cell in row
        if cell and len(cell.strip()) > 3
    ]
    if not cells:
        return True

    table_texts = " ".join(b.content for b in existing_blocks if b.block_type == "table")
    matches = sum(1 for cell in cells if cell in table_texts)
    return matches >= len(cells) * 0.5


def _extract_footnote_marker_and_text(footnote_text: str) -> tuple[str, str] | None:
    """Extract footnote marker and following body text."""
    clean = _strip_outer_markdown_emphasis(footnote_text)
    m = FOOTNOTE_PREFIX_REGEX.match(clean)
    if m:
        marker = m.group(2).strip()
        marker_clean = re.sub(r"<[^>]+>", "", marker)
        body = clean[m.end() :].strip()
        body = re.sub(r"^[:\-_*~`\s]+", "", body)
        return marker_clean, body
    return None


def _bind_footnotes_to_tables(page_blocks: list[ParsedBlock]) -> None:
    """Bind footnote text to corresponding table blocks on the same page."""
    tables = [b for b in page_blocks if b.block_type == "table"]
    footnotes = [b for b in page_blocks if b.block_type == "footnote"]
    if not tables or not footnotes:
        return

    parsed_footnotes: list[tuple[str, str]] = []
    for fn in footnotes:
        res = _extract_footnote_marker_and_text(fn.content)
        if res:
            parsed_footnotes.append(res)

    if not parsed_footnotes:
        return

    for table in tables:
        matching_bindings: list[tuple[str, str]] = []
        for marker, body in parsed_footnotes:
            if marker in table.raw_markdown or marker in table.content:
                matching_bindings.append((marker, body))

        # If only one table on the page, bind all page footnotes to it
        if not matching_bindings and len(tables) == 1:
            for marker, body in parsed_footnotes:
                matching_bindings.append((marker, body))

        if matching_bindings:
            seen: set[tuple[str, str]] = set()
            unique: list[tuple[str, str]] = []
            for m, b in matching_bindings:
                if (m, b) not in seen:
                    seen.add((m, b))
                    unique.append((m, b))

            footnotes_content = "\n\nFootnotes:\n" + "\n".join(
                f"- [{m}]: {b}" for m, b in unique
            )
            footnotes_md = "\n\n**Footnotes:**\n" + "\n".join(
                f"- **{m}**: {b}" for m, b in unique
            )
            table.content += footnotes_content
            table.raw_markdown += footnotes_md


_last_file_bytes: bytes | None = None
_last_visual_pages: list[int] = []


def page_has_minimal_text(page_markdown: str, threshold: int = 100) -> bool:
    """Check if a page's markdown text content is below a minimal threshold.

    Returns True if the page has fewer characters than threshold, indicating
    it is likely an infographic, image slide, or visual diagram.

    Args:
        page_markdown: Markdown or text representation of the page.
        threshold: Character count threshold (default 100).

    Returns:
        True if len(page_markdown.strip()) < threshold, False otherwise.
    """
    if not page_markdown:
        return True
    return len(page_markdown.strip()) < threshold


def render_page_as_image(
    file_bytes: bytes | None = None,
    page_number: int = 1,
) -> bytes:
    """Render a specific PDF page as a PNG image at 2x resolution.

    Args:
        file_bytes: Raw bytes of the PDF file. If None, uses the last parsed PDF bytes.
        page_number: 1-indexed page number to render.

    Returns:
        PNG image bytes.
    """
    global _last_file_bytes
    data = file_bytes if file_bytes is not None else _last_file_bytes
    if not data:
        logger.warning("No PDF file bytes available to render page %d", page_number)
        return b""

    with fitz.open(stream=data, filetype="pdf") as doc:
        if page_number < 1 or page_number > doc.page_count:
            logger.warning(
                "Page number %d out of range (1..%d)", page_number, doc.page_count
            )
            return b""
        page = doc[page_number - 1]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        return pixmap.tobytes("png")


def parse_pdf(
    file_bytes: bytes, filename: str = ""
) -> tuple[list[ParsedBlock], list[int]]:
    """Parse a PDF document into a sequence of layout-aware ParsedBlocks.

    Args:
        file_bytes: Raw bytes of the PDF file.
        filename: Optional filename for logging and tracking.

    Returns:
        Tuple of (all_blocks, visual_pages):
        - all_blocks: List of ParsedBlock instances labeled with page_number and block_type.
        - visual_pages: List of 1-indexed page numbers with minimal text (<100 chars)
          that likely require visual/multimodal extraction fallback.
    """
    global _last_file_bytes, _last_visual_pages
    if not file_bytes:
        logger.warning("Empty file bytes provided to parse_pdf: %s", filename)
        _last_file_bytes = None
        _last_visual_pages = []
        return [], []

    _last_file_bytes = file_bytes
    all_blocks: list[ParsedBlock] = []
    visual_pages: list[int] = []

    with fitz.open(stream=file_bytes, filetype="pdf") as doc, pdfplumber.open(
        io.BytesIO(file_bytes)
    ) as pdf:
        total_pages = doc.page_count
        logger.info(
            "Starting PDF parsing for %s (%d pages)", filename or "unnamed", total_pages
        )

        for page_idx in range(total_pages):
            page_num = page_idx + 1
            page_blocks: list[ParsedBlock] = []

            # Extract markdown representation preserving layout
            try:
                page_md = pymupdf4llm.to_markdown(doc, pages=[page_idx], use_ocr=False)
            except Exception as e:
                logger.warning(
                    "pymupdf4llm failed for page %d of %s: %s. Falling back to plain text.",
                    page_num,
                    filename,
                    e,
                )
                fitz_page = doc[page_idx]
                page_md = fitz_page.get_text("text")

            # Visual extraction path removed: all pages go through text extraction.
            # page_has_minimal_text() and visual_pages are kept for API compat but unused.

            # Split markdown into logical chunks
            chunks = [c.strip() for c in re.split(r"\n\s*\n+", page_md) if c.strip()]
            prev_block_type = ""

            for chunk_idx, chunk in enumerate(chunks):
                if _is_markdown_table(chunk):
                    b_type: Literal["text", "table", "footnote", "callout"] = "table"
                elif _is_footnote_block(chunk, chunk_idx, len(chunks), prev_block_type):
                    b_type = "footnote"
                elif _is_callout_block(chunk):
                    b_type = "callout"
                else:
                    b_type = "text"

                clean_content = _clean_markdown_to_text(chunk)
                block = ParsedBlock(
                    page_number=page_num,
                    block_type=b_type,
                    content=clean_content,
                    raw_markdown=chunk,
                )
                page_blocks.append(block)
                prev_block_type = b_type

            # Use pdfplumber to detect and extract any tables not captured in markdown
            if page_idx < len(pdf.pages):
                plumber_page = pdf.pages[page_idx]
                try:
                    plumber_tables = plumber_page.extract_tables() or []
                    for pt in plumber_tables:
                        if not _is_table_already_captured(pt, page_blocks):
                            content, raw_md = _format_plumber_table(pt)
                            if content and raw_md:
                                page_blocks.append(
                                    ParsedBlock(
                                        page_number=page_num,
                                        block_type="table",
                                        content=content,
                                        raw_markdown=raw_md,
                                    )
                                )
                except Exception as e:
                    logger.warning(
                        "pdfplumber table extraction failed on page %d: %s",
                        page_num,
                        e,
                    )

            # Bind footnotes to corresponding tables on this page
            _bind_footnotes_to_tables(page_blocks)

            all_blocks.extend(page_blocks)

    _last_visual_pages = list(visual_pages)
    logger.info(
        "PDF parsing complete (%d blocks, %d visual pages flagged) for %s",
        len(all_blocks),
        len(visual_pages),
        filename or "unnamed",
    )
    return all_blocks, visual_pages

import json
import uuid

import pytest

from app.services.extraction_service import ExtractionService
from app.services.pdf_parser import ParsedBlock


class FakeResponse:
    def __init__(self, payload: list[dict]) -> None:
        self.text = json.dumps(payload)


@pytest.mark.asyncio
async def test_extraction_uses_the_source_page_not_the_model_page() -> None:
    fact = {
        "subject": "Delhivery", "attribute": "revenue", "value_raw": "100 crore",
        "value_numeric": 100, "unit": "INR crore", "context_envelope": {},
        "evidence": {"verbatim_quote": "Delhivery revenue was 100 crore in FY24.", "page_number": 1, "section_title": None},
    }
    service = ExtractionService(client=object())
    service._call_gemini_generate = lambda *_: FakeResponse([fact])  # type: ignore[method-assign]
    blocks = [
        ParsedBlock(1, "text", "FY24 highlights", "FY24 highlights"),
        ParsedBlock(2, "text", "Delhivery revenue was 100 crore in FY24.", "Delhivery revenue was 100 crore in FY24."),
    ]

    extracted = await service.extract_facts(blocks, uuid.uuid4(), uuid.uuid4())

    assert len(extracted) == 1
    assert extracted[0]["evidence"]["page_number"] == 2


@pytest.mark.asyncio
async def test_extraction_rejects_ambiguous_quote_provenance() -> None:
    fact = {
        "subject": "Delhivery", "attribute": "revenue", "value_raw": "100 crore",
        "value_numeric": 100, "unit": "INR crore", "context_envelope": {},
        "evidence": {"verbatim_quote": "Revenue was 100 crore.", "page_number": 1, "section_title": None},
    }
    service = ExtractionService(client=object())
    service._call_gemini_generate = lambda *_: FakeResponse([fact])  # type: ignore[method-assign]
    blocks = [
        ParsedBlock(1, "text", "Revenue was 100 crore.", "Revenue was 100 crore."),
        ParsedBlock(2, "text", "Revenue was 100 crore.", "Revenue was 100 crore."),
    ]

    extracted = await service.extract_facts(blocks, uuid.uuid4(), uuid.uuid4())

    assert extracted == []

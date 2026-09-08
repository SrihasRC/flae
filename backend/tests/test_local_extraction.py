import pytest
from app.services.local_extraction import LocalExtractionService
from app.services.pdf_parser import ParsedBlock

@pytest.mark.asyncio
async def test_local_extraction_table_and_callouts():
    svc = LocalExtractionService()

    table_md = (
        "| Metric | FY23 | FY24 |\n"
        "| --- | --- | --- |\n"
        "| Revenue | ₹50,000 Mn | ₹72,000 Mn |\n"
        "| Adjusted EBITDA | 5.2% | 11.4% |\n"
    )

    blocks = [
        ParsedBlock(
            page_number=1,
            block_type="callout",
            content="₹40,000 Mn",
            raw_markdown="**₹40,000 Mn**",
        ),
        ParsedBlock(
            page_number=2,
            block_type="table",
            content="Revenue table",
            raw_markdown=table_md,
        ),
        ParsedBlock(
            page_number=3,
            block_type="text",
            content="Revenue from services grew by 18.2% YoY in Q4 FY24.",
            raw_markdown="Revenue from services grew by 18.2% YoY in Q4 FY24.",
        ),
    ]

    facts = await svc.extract_facts(
        blocks=blocks,
        document_id="doc-123",
        workspace_id="ws-456",
        filename="03-delhivery-q4-fy24-earnings.pdf",
    )

    assert len(facts) >= 5

    # Check callout fact
    callout_facts = [f for f in facts if f["evidence"]["page_number"] == 1]
    assert len(callout_facts) == 1
    assert callout_facts[0]["value_numeric"] == 40000.0
    assert callout_facts[0]["subject"] == "Delhivery"

    # Check table facts
    table_facts = [f for f in facts if f["evidence"]["page_number"] == 2]
    assert len(table_facts) == 4  # 2 rows x 2 data columns
    rev_fy24 = next(f for f in table_facts if "FY24" in f["attribute"] and "Revenue" in f["attribute"])
    assert rev_fy24["value_numeric"] == 72000.0

    # Check text fact
    text_facts = [f for f in facts if f["evidence"]["page_number"] == 3]
    assert len(text_facts) == 1
    assert text_facts[0]["value_numeric"] == 18.2
    assert text_facts[0]["context_envelope"]["temporal_period"] == "Q4 FY24"

import pytest
from types import SimpleNamespace
from app.services.arbitration_service import ArbitrationService

@pytest.mark.asyncio
async def test_deterministic_arbitration():
    svc = ArbitrationService(
        embedding_service=SimpleNamespace(),
        vector_store=SimpleNamespace(),
        fact_repo=SimpleNamespace(),
    )

    fact_a = {
        "fact_id": "fact-1",
        "document_id": "doc-1",
        "workspace_id": "ws-1",
        "subject": "Delhivery",
        "attribute": "Revenue from operations — FY24",
        "value_raw": "₹81,420 Mn",
        "value_numeric": 81420.0,
        "context_envelope": {"temporal_period": "FY24"},
        "evidence": {"verbatim_quote": "Revenue was ₹81,420 Mn", "page_number": 5},
    }

    fact_b = {
        "fact_id": "fact-2",
        "document_id": "doc-2",
        "workspace_id": "ws-1",
        "subject": "Delhivery",
        "attribute": "Revenue from operations — FY24",
        "value_raw": "₹81,420 Mn",
        "value_numeric": 81420.0,
        "context_envelope": {"temporal_period": "FY24"},
        "evidence": {"verbatim_quote": "Operations revenue: ₹81,420 Mn", "page_number": 12},
    }

    result = await svc.arbitrate_pair(fact_a, fact_b)
    assert result["relationship"] == "CORROBORATED"
    assert result["confidence_score"] == 1.0
    assert "Deterministic corroboration" in result["reasoning_trace"]
    assert result["fact_a_id"] == "fact-1"
    assert result["fact_b_id"] == "fact-2"

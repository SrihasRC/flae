"""Arbitrate key macro cases for india-macroeconomy workspace.

Extracts/inserts the exact CPI and GDP facts from the source documents:
1. Doc 1 (Economic Survey 2024-25 Excerpt, page 28): Headline CPI inflation in FY24 = 5.4%
2. Doc 2 (RBI Annual Report 2024-25 Excerpt, page 38): Headline CPI inflation in 2023-24 = 5.4%
-> Results in CORROBORATED (Case 1)

3. Doc 1 (Economic Survey 2024-25 Excerpt, page 20): Q1 FY25 Real GDP Growth = 6.7%
4. Doc 2 (RBI Annual Report 2024-25 Excerpt, page 24): Q1:2024-25 Real GDP Growth = 6.5%
-> Results in CONTRADICTED (Case 2)

5. Doc 1 (Economic Survey 2024-25 Excerpt, page 20): Q2 FY25 Real GDP Growth = 5.4%
6. Doc 2 (RBI Annual Report 2024-25 Excerpt, page 24): Q2:2024-25 Real GDP Growth = 5.6%
-> Results in CONTRADICTED (Case 2)
"""

import asyncio
import logging
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import AsyncSessionLocal
from app.repositories.arbitration_repository import ArbitrationRepository
from app.repositories.fact_repository import FactRepository
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.arbitration_service import ArbitrationService, _fact_to_dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("macro_arbitration")

WORKSPACE_ID = uuid.UUID("95f70b45-efd6-416b-a60a-69531b54da64")
DOC_ES_ID = uuid.UUID("96a64537-e1b3-410f-8e24-e7a52797293d")
DOC_RBI_ID = uuid.UUID("8eff99a0-fe74-4470-93ec-9cb71b70e612")

FACTS_TO_REGISTER = [
    # ES CPI Fact
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555501"),
        "workspace_id": WORKSPACE_ID,
        "document_id": DOC_ES_ID,
        "subject": "Headline Inflation (CPI)",
        "attribute": "Headline CPI inflation rate in FY24",
        "value_raw": "5.4%",
        "value_numeric": 5.4,
        "unit": "%",
        "context_envelope": {
            "temporal_period": "FY24",
            "geography": "India",
            "entity_scope": "National",
            "period_type": "fiscal_year",
        },
        "evidence": {
            "page_number": 28,
            "verbatim_quote": "Headline inflation, based on the Consumer Price Index (CPI), has softened from 5.4 per cent in FY24 to 4.9 per cent in April – December 2024.",
            "section_title": "Inflation",
        },
    },
    # RBI CPI Fact
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555502"),
        "workspace_id": WORKSPACE_ID,
        "document_id": DOC_RBI_ID,
        "subject": "Headline Inflation (CPI)",
        "attribute": "Headline CPI inflation rate in 2023-24 (FY24)",
        "value_raw": "5.4%",
        "value_numeric": 5.4,
        "unit": "%",
        "context_envelope": {
            "temporal_period": "2023-24",
            "geography": "India",
            "entity_scope": "National",
            "period_type": "fiscal_year",
        },
        "evidence": {
            "page_number": 38,
            "verbatim_quote": "Headline inflation moderated to an average of 4.6 per cent during 2024-25 from 5.4 per cent in the previous year (2023-24).",
            "section_title": "Price Situation",
        },
    },
    # ES Q1 GDP Fact
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555503"),
        "workspace_id": WORKSPACE_ID,
        "document_id": DOC_ES_ID,
        "subject": "Real GDP Growth",
        "attribute": "Real GDP growth rate at constant (2011-12) prices in Q1 FY25",
        "value_raw": "6.7%",
        "value_numeric": 6.7,
        "unit": "%",
        "context_envelope": {
            "temporal_period": "Q1 FY25",
            "geography": "India",
            "entity_scope": "National",
            "period_type": "quarterly",
        },
        "evidence": {
            "page_number": 20,
            "verbatim_quote": "India’s GDP at constant (2011-12) prices grew by 6.7 per cent and 5.4 per cent in Q1 and Q2 FY25, respectively.",
            "section_title": "Economic Growth",
        },
    },
    # RBI Q1 GDP Fact
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555504"),
        "workspace_id": WORKSPACE_ID,
        "document_id": DOC_RBI_ID,
        "subject": "Real GDP Growth",
        "attribute": "Real GDP growth rate at constant (2011-12) prices in Q1 FY25",
        "value_raw": "6.5%",
        "value_numeric": 6.5,
        "unit": "%",
        "context_envelope": {
            "temporal_period": "Q1 FY25",
            "geography": "India",
            "entity_scope": "National",
            "period_type": "quarterly",
        },
        "evidence": {
            "page_number": 24,
            "verbatim_quote": "quarterly trajectory, real GDP rose (y-o-y) by 6.5 per cent in Q1:2024-25; growth softened to 5.6 per cent in Q2",
            "section_title": "Economic Review",
        },
    },
    # ES Q2 GDP Fact
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555505"),
        "workspace_id": WORKSPACE_ID,
        "document_id": DOC_ES_ID,
        "subject": "Real GDP Growth",
        "attribute": "Real GDP growth rate at constant (2011-12) prices in Q2 FY25",
        "value_raw": "5.4%",
        "value_numeric": 5.4,
        "unit": "%",
        "context_envelope": {
            "temporal_period": "Q2 FY25",
            "geography": "India",
            "entity_scope": "National",
            "period_type": "quarterly",
        },
        "evidence": {
            "page_number": 20,
            "verbatim_quote": "India’s GDP at constant (2011-12) prices grew by 6.7 per cent and 5.4 per cent in Q1 and Q2 FY25, respectively.",
            "section_title": "Economic Growth",
        },
    },
    # RBI Q2 GDP Fact
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555506"),
        "workspace_id": WORKSPACE_ID,
        "document_id": DOC_RBI_ID,
        "subject": "Real GDP Growth",
        "attribute": "Real GDP growth rate at constant (2011-12) prices in Q2 FY25",
        "value_raw": "5.6%",
        "value_numeric": 5.6,
        "unit": "%",
        "context_envelope": {
            "temporal_period": "Q2 FY25",
            "geography": "India",
            "entity_scope": "National",
            "period_type": "quarterly",
        },
        "evidence": {
            "page_number": 24,
            "verbatim_quote": "growth softened to 5.6 per cent in Q2, inter alia, on excess rainfall which dampened mining output and electricity demand",
            "section_title": "Economic Review",
        },
    },
]


async def main():
    async with AsyncSessionLocal() as session:
        fact_repo = FactRepository(session)
        arb_repo = ArbitrationRepository(session)
        emb_svc = EmbeddingService()
        vec_store = VectorStoreService()
        arb_svc = ArbitrationService(
            embedding_service=emb_svc,
            vector_store=vec_store,
            fact_repo=fact_repo,
        )

        logger.info("Ensuring high-precision facts in database...")
        for fact_dict in FACTS_TO_REGISTER:
            existing = await fact_repo.get_by_id(fact_dict["id"])
            if not existing:
                created = await fact_repo.create(fact_dict)
                logger.info("Created fact: %s -> %s = %s", created.id, created.attribute, created.value_raw)
            else:
                logger.info("Fact %s already exists.", fact_dict["id"])

        await session.commit()

        # Fetch fresh instances
        f1 = await fact_repo.get_by_id(uuid.UUID("11111111-2222-3333-4444-555555555501"))
        f2 = await fact_repo.get_by_id(uuid.UUID("11111111-2222-3333-4444-555555555502"))
        f3 = await fact_repo.get_by_id(uuid.UUID("11111111-2222-3333-4444-555555555503"))
        f4 = await fact_repo.get_by_id(uuid.UUID("11111111-2222-3333-4444-555555555504"))
        f5 = await fact_repo.get_by_id(uuid.UUID("11111111-2222-3333-4444-555555555505"))
        f6 = await fact_repo.get_by_id(uuid.UUID("11111111-2222-3333-4444-555555555506"))

        pairs = [
            ("Case 1 (CORROBORATED CPI 5.4%)", f1, f2),
            ("Case 2 (CONTRADICTED Q1 GDP 6.7% vs 6.5%)", f3, f4),
            ("Case 2 (CONTRADICTED Q2 GDP 5.4% vs 5.6%)", f5, f6),
        ]

        new_arbs = []
        for label, fa, fb in pairs:
            logger.info("Arbitrating pair: %s", label)
            logger.info("  Fact A: %s | %s | %s", fa.subject, fa.attribute, fa.value_raw)
            logger.info("  Fact B: %s | %s | %s", fb.subject, fb.attribute, fb.value_raw)

            res = await arb_svc.arbitrate_pair(
                fact_a=fa,
                fact_b=fb,
            )

            rel = res.get("relationship")
            conf = res.get("confidence_score")
            reason = res.get("reasoning_trace")

            logger.info("  -> Result: %s (conf %s)", rel, conf)
            logger.info("  -> Reasoning: %s", reason[:200] if reason else "")

            arb_dict = {
                "arbitration_id": uuid.uuid4(),
                "fact_a_id": fa.id,
                "fact_b_id": fb.id,
                "workspace_id": WORKSPACE_ID,
                "relationship": rel,
                "divergence_factor": res.get("divergence_factor"),
                "confidence_score": conf,
                "reasoning_trace": reason,
                "evidence_comparison": res.get("evidence_comparison") or {},
            }
            new_arbs.append(arb_dict)
            await asyncio.sleep(5.0)

        saved = await arb_repo.create_bulk(new_arbs)
        await session.commit()
        logger.info("Successfully persisted %d new arbitrations to database!", len(saved))


if __name__ == "__main__":
    asyncio.run(main())

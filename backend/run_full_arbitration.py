"""Full monitored cross-document arbitration pipeline.

- Adheres strictly to Groq rate limits (5.0s pacing, automatic 20s retry backoff).
- Uses openai/gpt-oss-120b with max_tokens=1500 to prevent JSON truncation.
- Uses deterministic fast-path for exact matches.
- Cleans previous fallback records.
- Populates PostgreSQL arbitrations table for frontend Case Explorer.
"""

import asyncio
import logging
import sys
from pathlib import Path
import uuid
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import AsyncSessionLocal
from app.repositories.arbitration_repository import ArbitrationRepository
from app.repositories.fact_repository import FactRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.arbitration_service import ArbitrationService, _fact_to_dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("arbitration_runner")

WORKSPACE_ID = uuid.UUID("b097fafc-4e75-442d-8065-b4cee73091b9")

async def main():
    async with AsyncSessionLocal() as session:
        # Step 1: Clean up any fallback records from previous runs
        del_stmt = text(
            "DELETE FROM arbitrations WHERE workspace_id = :ws_id AND confidence_score = 0.0 AND reasoning_trace LIKE 'Fallback%';"
        )
        res = await session.execute(del_stmt, {"ws_id": WORKSPACE_ID})
        await session.commit()
        logger.info("Cleaned %d fallback records from database.", res.rowcount)

        fact_repo = FactRepository(session)
        arb_repo = ArbitrationRepository(session)
        emb_svc = EmbeddingService()
        vec_store = VectorStoreService()
        arb_svc = ArbitrationService(emb_svc, vec_store, fact_repo)

        # Ensure pacing is safe for Groq 8,000 TPM
        arb_svc.CALL_INTERVAL_SECONDS = 5.0

        # Load existing arbitrated pairs so we never duplicate
        existing_arbs = await arb_repo.list_by_workspace(WORKSPACE_ID, skip=0, limit=1000)
        seen_pairs = set()
        for a in existing_arbs:
            seen_pairs.add(frozenset([str(a.fact_a_id), str(a.fact_b_id)]))
        logger.info("Loaded %d existing arbitration records.", len(seen_pairs))

        # Run arbitration for workspace
        target_new_pairs = 30
        logger.info("Targeting up to %d high-quality cross-document pairs...", target_new_pairs)

        facts = await fact_repo.list_by_workspace(WORKSPACE_ID, skip=0, limit=5000)
        logger.info("Loaded %d total facts in workspace.", len(facts))

        # Prioritize facts with high epistemic value (financial, volumes, network reach, governance)
        kpi_terms = [
            "revenue", "ebitda", "profit", "loss", "pat", "pbt", "expense", "margin",
            "pin-code", "reach", "shares", "equity", "tonnage", "shipments", "parcel",
            "truckload", "supply chain", "express", "may 17", "2024", "2022", "2023"
        ]
        kpi_facts = [f for f in facts if any(term in f.attribute.lower() or term in f.value_raw.lower() for term in kpi_terms)]
        other_facts = [f for f in facts if f not in kpi_facts]
        ordered_facts = kpi_facts + other_facts
        logger.info("Prioritized %d KPI facts for candidate discovery.", len(kpi_facts))

        new_results = []
        for fact in ordered_facts:
            if len(new_results) >= target_new_pairs:
                logger.info("Reached target of %d new arbitrations. Concluding run.", target_new_pairs)
                break

            fact_a_dict = _fact_to_dict(fact)
            fact_a_id = str(fact_a_dict.get("fact_id", ""))
            subject = str(fact_a_dict.get("subject", ""))
            attribute = str(fact_a_dict.get("attribute", ""))
            doc_id = str(fact_a_dict.get("document_id", ""))

            if not fact_a_id or not subject or not attribute:
                continue

            emb = await emb_svc.embed_fact_anchor(subject, attribute)
            candidates = vec_store.query_candidates(
                workspace_id=WORKSPACE_ID,
                embedding=emb,
                exclude_document_id=doc_id,
                top_k=5,
                threshold=0.84,
            )

            for cand in candidates:
                if len(new_results) >= target_new_pairs:
                    break

                cand_fact_id = str(cand.get("fact_id", ""))
                if not cand_fact_id or cand_fact_id == fact_a_id:
                    continue

                pair_key = frozenset([fact_a_id, cand_fact_id])
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                fact_b = await fact_repo.get_by_id(cand_fact_id)
                if not fact_b:
                    continue
                fact_b_dict = _fact_to_dict(fact_b)

                try:
                    result = await arb_svc.arbitrate_pair(fact_a_dict, fact_b_dict)
                    # Only accept real adjudications (not fallback)
                    if result["confidence_score"] > 0.0 or not result["reasoning_trace"].startswith("Fallback"):
                        new_results.append(result)
                        # Save incrementally to database
                        await arb_repo.create_bulk([dict(result) | {"workspace_id": str(WORKSPACE_ID)}])
                        await session.commit()
                        logger.info(
                            "Arbitrated & Saved [%d/%d]: %s vs %s -> %s (conf: %.2f) | %s",
                            len(new_results),
                            target_new_pairs,
                            fact_a_id[:8],
                            cand_fact_id[:8],
                            result["relationship"],
                            result["confidence_score"],
                            result["reasoning_trace"][:75],
                        )
                except Exception as err:
                    logger.error("Error arbitrating pair %s vs %s: %s", fact_a_id[:8], cand_fact_id[:8], err)

        # Final Summary
        logger.info("\n=== ARBITRATION RUN COMPLETE ===")
        case_1 = await arb_repo.list_by_relationship(WORKSPACE_ID, "CORROBORATED")
        case_2 = await arb_repo.list_by_relationship(WORKSPACE_ID, "CONTRADICTED")
        case_3 = await arb_repo.list_by_relationship(WORKSPACE_ID, "RECONCILED")
        case_4 = await arb_repo.list_by_relationship(WORKSPACE_ID, "UNRELATED")
        total = await arb_repo.count_by_workspace(WORKSPACE_ID)

        print("\n=======================================================")
        print(f"WORKSPACE ARBITRATION SUMMARY (Total in DB: {total})")
        print("=======================================================")
        print(f"  Case 1 (CORROBORATED): {len(case_1)} records")
        print(f"  Case 2 (CONTRADICTED): {len(case_2)} records")
        print(f"  Case 3 (RECONCILED):   {len(case_3)} records")
        print(f"  Case 4 (UNRELATED):    {len(case_4)} records")
        print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())

from __future__ import annotations

import json
import shutil
from pathlib import Path

import fitz

import control_tower.service as service_module
from control_tower.processing.models import PageAnalysis
from control_tower.service import ControlTowerService


class DeterministicCloudProof:
    provider_name = "adaptive_router"

    def analyze_batch(self, pages, profiles):
        return [
            PageAnalysis(
                page_number=page.page_number,
                provider="proof_cloud",
                summary="Schéma et annotation analysés.",
                extracted_text="Annotation manuscrite détectée: fermer la vanne rouge.",
                handwriting_text="fermer la vanne rouge",
                concepts=["vanne", "sécurité"],
                pseudocode=["FERMER vanne_rouge"],
                maieutic_questions=["Pourquoi cette vanne est-elle critique ?"],
                kant_tensions=["means_vs_ends"],
                confidence=0.97,
                needs_multimodal_review=False,
            )
            for page in pages
        ]

    def report(self):
        return {
            "profile": "cloud_turbo",
            "deferred_pages": [],
            "routes": {"1": {"selected_provider": "proof_cloud"}},
            "providers": [],
            "budget": {"maximum_usd": 15, "estimated_spent_usd": 0.01},
            "proof_note": "Provider simulé; pipeline, artefacts et réindexation réels.",
        }


def make_pdf(path: Path) -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((50, 80), "Procédure hydraulique.")
    page.draw_line((50, 130), (250, 130), width=2)
    page.draw_rect(fitz.Rect(250, 105, 390, 165), width=2)
    document.save(path)
    document.close()


def main() -> None:
    root = Path(".proof_alternative").resolve()
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    source = root / "document_visuel.pdf"
    make_pdf(source)

    service = ControlTowerService(root / "workspace")
    service.init_project("demo")
    plan = service.plan_document("demo", source)
    ingestion = service.ingest("demo", source)
    document_id = ingestion["data"]["document_id"]
    initial = service.inspect_document("demo", document_id)

    original_builder = service_module.build_vision_analyzer
    service_module.build_vision_analyzer = lambda config: DeterministicCloudProof()
    try:
        enrichment = service.enrich_document("demo", document_id, "cloud_turbo")
    finally:
        service_module.build_vision_analyzer = original_builder

    query = service.query("demo", "vanne rouge", top_k=5)
    final = service.inspect_document("demo", document_id)
    proof = {
        "plan": plan["vision_plan"]["counts"],
        "document_id": document_id,
        "initial_deferred_pages": initial["processing"]["provider_report.json"]["deferred_pages"],
        "enrichment_status": enrichment["status"],
        "enriched_pages": enrichment["enriched_pages"],
        "remaining_review_pages": enrichment["remaining_review_pages"],
        "query_hit_count": len(query["hits"]),
        "query_first_text": query["hits"][0]["chunk"]["text"] if query["hits"] else None,
        "document_count_after_enrichment": service.inspect_project("demo")["store"]["documents"],
        "final_provider": final["processing"]["page_analyses.json"]["1"]["provider"],
        "note": "Le provider cloud est simulé; tout le cycle différé et la réindexation sont réels.",
    }
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

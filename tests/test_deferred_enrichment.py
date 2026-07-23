from pathlib import Path

import fitz

from control_tower.processing.models import PageAnalysis
from control_tower.service import ControlTowerService
from control_tower.storage.sqlite import SQLiteStore


class FakeCloudAnalyzer:
    provider_name = "adaptive_router"

    def analyze_batch(self, pages, profiles):
        return [
            PageAnalysis(
                page_number=page.page_number,
                provider="fake_cloud",
                summary="Schéma de maintenance analysé.",
                extracted_text="Annotation manuscrite: vanne secrète à fermer.",
                handwriting_text="vanne secrète à fermer",
                concepts=["vanne", "maintenance"],
                pseudocode=["FERMER vanne_secrete"],
                maieutic_questions=["Pourquoi fermer cette vanne ?"],
                kant_tensions=["means_vs_ends"],
                confidence=0.95,
                needs_multimodal_review=False,
            )
            for page in pages
        ]

    def report(self):
        return {
            "profile": "cloud_turbo",
            "deferred_pages": [],
            "routes": {"1": {"selected_provider": "fake_cloud"}},
            "providers": [],
            "budget": {"maximum_usd": 10, "estimated_spent_usd": 0.01},
        }


def make_visual_pdf(path: Path) -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((50, 80), "Procédure de maintenance du circuit hydraulique.")
    page.draw_line((50, 120), (300, 120), width=2)
    page.draw_rect(fitz.Rect(300, 100, 400, 160), width=2)
    document.save(path)
    document.close()


def test_deferred_pages_can_be_enriched_without_duplicating_document(tmp_path: Path, monkeypatch):
    source = tmp_path / "visual.pdf"
    make_visual_pdf(source)
    service = ControlTowerService(tmp_path / "workspace")
    service.init_project("demo")

    ingestion = service.ingest("demo", source)
    document_id = ingestion["data"]["document_id"]
    report = ingestion["data"]["artifacts"]["provider_report"]
    assert report is not None

    monkeypatch.setattr("control_tower.service.build_vision_analyzer", lambda config: FakeCloudAnalyzer())
    enriched = service.enrich_document("demo", document_id, "cloud_turbo")

    assert enriched["status"] == "enriched"
    assert enriched["enriched_pages"] == [1]
    assert enriched["remaining_review_pages"] == []

    query = service.query("demo", "vanne secrète", top_k=5)
    assert query["hits"]
    assert query["hits"][0]["chunk"]["document_id"] == document_id

    store = SQLiteStore(tmp_path / "workspace" / "demo" / "state" / "knowledge.db")
    assert store.stats()["documents"] == 1


def test_multimodal_merge_does_not_duplicate_handwriting_subset():
    from control_tower.ingestion.pipeline import IngestionPipeline
    from control_tower.ocr.models import ExtractedPage, ExtractionMethod

    pages = [
        ExtractedPage(
            page_number=1,
            text="Texte de base.",
            method=ExtractionMethod.NATIVE_PDF,
        )
    ]
    analyses = {
        1: PageAnalysis(
            page_number=1,
            provider="cloud",
            extracted_text="Annotation manuscrite: fermer la vanne rouge.",
            handwriting_text="fermer la vanne rouge",
        )
    }

    IngestionPipeline._merge_multimodal_text(pages, analyses)

    assert pages[0].text.count("fermer la vanne rouge") == 1

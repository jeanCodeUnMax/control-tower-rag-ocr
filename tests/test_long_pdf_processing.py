from pathlib import Path

import fitz

from control_tower.config import ProjectConfig
from control_tower.ocr.pdf import PDFOCRProvider
from control_tower.processing.executor import LongPDFProcessor
from control_tower.processing.vision import LocalVisionAnalyzer
from control_tower.service import ControlTowerService
from control_tower.storage.sqlite import SQLiteStore


def make_pdf(path: Path, pages: int, repeated: bool = False) -> None:
    document = fitz.open()
    for number in range(1, pages + 1):
        page = document.new_page()
        body = (
            "Procédure de sécurité répétée. Vérifier le capteur, arrêter la machine, "
            "puis enregistrer le contrôle dans le registre de maintenance."
            if repeated
            else (
                f"Page {number}. Procédure de sécurité numéro {number}. "
                "Vérifier le capteur, analyser le signal et enregistrer le résultat."
            )
        )
        page.insert_textbox(fitz.Rect(50, 50, 540, 760), body, fontsize=11)
    document.save(path)
    document.close()


class SplitUntilSingleProvider(PDFOCRProvider):
    def extract_pages(self, source, config, page_numbers):
        if 3 in page_numbers and len(page_numbers) > 1:
            raise RuntimeError("Lot artificiellement trop lourd")
        return super().extract_pages(source, config, page_numbers)


class PermanentPageFailureProvider(PDFOCRProvider):
    def extract_pages(self, source, config, page_numbers):
        if 4 in page_numbers:
            raise RuntimeError("Page 4 illisible")
        return super().extract_pages(source, config, page_numbers)


def test_batch_failure_is_split_until_the_problem_page_is_isolated(tmp_path: Path):
    source = tmp_path / "six-pages.pdf"
    make_pdf(source, 6)
    config = ProjectConfig()
    config.batching.max_pages = 5
    config.batching.retry_limit = 3
    result = LongPDFProcessor(
        config,
        pdf_provider=SplitUntilSingleProvider(),
        vision_analyzer=LocalVisionAnalyzer(),
    ).process(source, "doc-split", tmp_path / "artifacts")

    assert result.complete is True
    assert result.ledger.completed_pages == [1, 2, 3, 4, 5, 6]
    assert result.ledger.failed_pages == []
    assert result.ledger.failed_batches
    assert any(batch.parent_batch_id for batch in result.ledger.planned_batches)


def test_permanent_page_failure_is_visible_and_document_is_not_complete(tmp_path: Path):
    source = tmp_path / "five-pages.pdf"
    make_pdf(source, 5)
    config = ProjectConfig()
    config.batching.max_pages = 5
    config.batching.retry_limit = 1
    result = LongPDFProcessor(
        config,
        pdf_provider=PermanentPageFailureProvider(),
        vision_analyzer=LocalVisionAnalyzer(),
    ).process(source, "doc-fail", tmp_path / "artifacts")

    assert result.complete is False
    assert result.ledger.failed_pages == [4]
    assert result.ledger.missing_pages == []
    assert result.ledger.completed_pages == [1, 2, 3, 5]


def test_pipeline_consolidates_repeated_pages_and_searches_only_canonical(tmp_path: Path):
    source = tmp_path / "repeated.pdf"
    make_pdf(source, 20, repeated=True)
    service = ControlTowerService(tmp_path / "workspace")
    service.init_project("demo")

    result = service.ingest("demo", source)

    assert result["status"] == "ok"
    assert result["data"]["ledger"]["complete"] is True
    assert result["data"]["ledger"]["completed_pages"] == 20
    assert result["data"]["chunk_count"] == 20
    assert result["data"]["canonical_chunk_count"] == 1

    store = SQLiteStore(tmp_path / "workspace" / "demo" / "state" / "knowledge.db")
    chunks = store.chunks_for_document(result["data"]["document_id"])
    canonical = [chunk for chunk in chunks if chunk.indexable]
    duplicates = [chunk for chunk in chunks if not chunk.indexable]
    assert len(canonical) == 1
    assert len(duplicates) == 19
    assert len(canonical[0].evidence_occurrences) == 20

    query = service.query("demo", "arrêter la machine sécurité", top_k=20)
    assert len(query["hits"]) == 1

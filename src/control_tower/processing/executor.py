from __future__ import annotations

import json
import shutil
from pathlib import Path

from control_tower.config import ProjectConfig
from control_tower.ocr.models import ExtractionResult
from control_tower.ocr.pdf import PDFOCRProvider
from control_tower.processing.assets import extract_visual_assets
from control_tower.processing.batching import AdaptiveBatchPlanner
from control_tower.processing.models import (
    IngestionLedger,
    LongPDFResult,
    PageAnalysis,
    PageBatch,
    PageLedgerEntry,
    PageProfile,
    PageState,
    RenderedPage,
    VisualAsset,
)
from control_tower.processing.rendering import render_pdf_pages
from control_tower.processing.vision import VisionAnalyzer, build_vision_analyzer


class LongPDFProcessor:
    """Traite un PDF par lots bornés avec checkpoint et contrôle de complétude."""

    def __init__(
        self,
        config: ProjectConfig,
        *,
        pdf_provider: PDFOCRProvider | None = None,
        vision_analyzer: VisionAnalyzer | None = None,
    ) -> None:
        self.config = config
        self.pdf_provider = pdf_provider or PDFOCRProvider()
        self.vision_analyzer = vision_analyzer or build_vision_analyzer(config.vision)
        self.planner = AdaptiveBatchPlanner(config.batching)

    def process(self, source: Path, document_id: str, artifact_dir: Path) -> LongPDFResult:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        pages_dir = artifact_dir / "pages"
        batches_dir = artifact_dir / "batches"
        renders_dir = artifact_dir / "renders"
        assets_dir = artifact_dir / "visual_assets"
        for directory in (pages_dir, batches_dir, renders_dir, assets_dir):
            directory.mkdir(parents=True, exist_ok=True)

        profiles = self.pdf_provider.profile(source, self.config.ocr, self.config.batching)
        profile_map = {profile.page_number: profile for profile in profiles}
        batches = self.planner.plan(profiles)
        ledger = IngestionLedger(
            document_id=document_id,
            source_name=source.name,
            total_pages=len(profiles),
            entries={
                profile.page_number: PageLedgerEntry(page_number=profile.page_number)
                for profile in profiles
            },
            planned_batches=list(batches),
        )
        self._write_json(
            artifact_dir / "page_profiles.json",
            [profile.model_dump(mode="json") for profile in profiles],
        )
        self._write_json(
            artifact_dir / "batch_plan.json",
            [batch.model_dump(mode="json") for batch in batches],
        )
        self._checkpoint(artifact_dir, ledger)

        extracted_by_page = {}
        analyses: dict[int, PageAnalysis] = {}
        assets: list[VisualAsset] = []
        queue = list(batches)

        while queue:
            batch = queue.pop(0)
            for page_number in batch.page_numbers:
                entry = ledger.entries[page_number]
                entry.state = PageState.PROCESSING
                entry.attempts += 1
                entry.batch_ids.append(batch.id)
                entry.error = None
            self._checkpoint(artifact_dir, ledger)

            try:
                extraction = self.pdf_provider.extract_pages(
                    source,
                    self.config.ocr,
                    batch.page_numbers,
                )
                if {page.page_number for page in extraction.pages} != set(batch.page_numbers):
                    raise RuntimeError(
                        "Extraction incomplète du lot: "
                        f"attendu={batch.page_numbers}, "
                        f"reçu={[page.page_number for page in extraction.pages]}"
                    )

                batch_assets = extract_visual_assets(
                    source,
                    document_id,
                    batch.page_numbers,
                    assets_dir,
                )
                rendered = self._prepare_rendered_pages(
                    source,
                    extraction,
                    batch,
                    profile_map,
                    renders_dir,
                )
                batch_analyses = self.vision_analyzer.analyze_batch(rendered, profile_map)
                analysis_by_page = {analysis.page_number: analysis for analysis in batch_analyses}
                if set(analysis_by_page) != set(batch.page_numbers):
                    raise RuntimeError(
                        "Analyse visuelle incomplète du lot: "
                        f"attendu={batch.page_numbers}, reçu={sorted(analysis_by_page)}"
                    )

                assets_by_page: dict[int, list[VisualAsset]] = {}
                for asset in batch_assets:
                    assets_by_page.setdefault(asset.page_number, []).append(asset)

                for page in extraction.pages:
                    page_number = page.page_number
                    analysis = analysis_by_page[page_number]
                    page_assets = assets_by_page.get(page_number, [])
                    artifact_path = pages_dir / f"page_{page_number:05d}.json"
                    self._write_json(
                        artifact_path,
                        {
                            "profile": profile_map[page_number].model_dump(mode="json"),
                            "extraction": page.model_dump(mode="json"),
                            "analysis": analysis.model_dump(mode="json"),
                            "visual_assets": [
                                asset.model_dump(mode="json") for asset in page_assets
                            ],
                            "batch": batch.model_dump(mode="json"),
                        },
                    )
                    extracted_by_page[page_number] = page
                    analyses[page_number] = analysis
                    entry = ledger.entries[page_number]
                    entry.state = PageState.COMPLETED
                    entry.extraction_method = page.method.value
                    entry.artifact_path = str(artifact_path)
                    entry.error = None

                assets.extend(batch_assets)
                ledger.completed_batches.append(batch.id)
                self._write_json(
                    batches_dir / f"batch_{batch.start_page:05d}_{batch.end_page:05d}_{batch.id}.json",
                    {
                        "status": "completed",
                        "batch": batch.model_dump(mode="json"),
                        "pages": batch.page_numbers,
                        "methods": extraction.methods,
                        "warnings": extraction.warnings,
                    },
                )
            except Exception as exc:
                ledger.failed_batches.append(batch.id)
                self._write_json(
                    batches_dir / f"batch_{batch.start_page:05d}_{batch.end_page:05d}_{batch.id}.json",
                    {
                        "status": "failed",
                        "batch": batch.model_dump(mode="json"),
                        "error": str(exc),
                    },
                )
                retry_batches = self._retry_batches(batch)
                if retry_batches:
                    for page_number in batch.page_numbers:
                        entry = ledger.entries[page_number]
                        entry.state = PageState.PENDING
                        entry.error = str(exc)
                    ledger.planned_batches.extend(retry_batches)
                    queue = retry_batches + queue
                else:
                    for page_number in batch.page_numbers:
                        entry = ledger.entries[page_number]
                        entry.state = PageState.FAILED
                        entry.error = str(exc)
            finally:
                self._checkpoint(artifact_dir, ledger)

        ordered_pages = [extracted_by_page[number] for number in sorted(extracted_by_page)]
        extraction_result = ExtractionResult(
            source_path=str(source),
            source_type="pdf",
            pages=ordered_pages,
            warnings=[
                f"Pages en échec: {ledger.failed_pages}" if ledger.failed_pages else ""
            ],
            metadata={
                "pdf_page_count": ledger.total_pages,
                "batching": self.config.batching.model_dump(mode="json"),
                "ledger_summary": ledger.summary(),
            },
        )
        extraction_result.warnings = [item for item in extraction_result.warnings if item]
        self._write_json(
            artifact_dir / "page_analyses.json",
            {
                str(number): analysis.model_dump(mode="json")
                for number, analysis in sorted(analyses.items())
            },
        )
        self._write_json(
            artifact_dir / "visual_assets.json",
            [asset.model_dump(mode="json") for asset in assets],
        )
        report = getattr(self.vision_analyzer, "report", None)
        if callable(report):
            self._write_json(artifact_dir / "provider_report.json", report())
        return LongPDFResult(
            extraction=extraction_result,
            analyses=analyses,
            assets=assets,
            ledger=ledger,
            artifact_dir=str(artifact_dir),
        )

    def _prepare_rendered_pages(
        self,
        source: Path,
        extraction: ExtractionResult,
        batch: PageBatch,
        profiles: dict[int, PageProfile],
        renders_dir: Path,
    ) -> list[RenderedPage]:
        extraction_by_page = {page.page_number: page for page in extraction.pages}
        provider_name = getattr(self.vision_analyzer, "provider_name", "local")
        render_numbers: list[int] = []
        if self.config.vision.enabled and provider_name != "local":
            if provider_name == "adaptive_router":
                from control_tower.processing.routing import route_page

                render_numbers = [
                    page_number
                    for page_number in batch.page_numbers
                    if route_page(profiles[page_number], self.config.vision) == "cloud"
                ]
            else:
                render_numbers = list(batch.page_numbers)

        rendered_by_page: dict[int, RenderedPage] = {}
        if render_numbers:
            rendered = render_pdf_pages(
                source,
                render_numbers,
                renders_dir,
                dpi=self.config.vision.render_dpi,
                profiles=profiles,
            )
            rendered_by_page = {
                page.page_number: page.model_copy(
                    update={"native_text": extraction_by_page[page.page_number].text}
                )
                for page in rendered
            }

        return [
            rendered_by_page.get(
                page_number,
                RenderedPage(
                    page_number=page_number,
                    image_path=source,
                    native_text=extraction_by_page[page_number].text,
                    image_count=profiles[page_number].image_count,
                    drawing_count=profiles[page_number].drawing_count,
                ),
            )
            for page_number in batch.page_numbers
        ]

    def _retry_batches(self, batch: PageBatch) -> list[PageBatch]:
        # La division n'est pas un simple retry : elle sert à isoler la page fautive.
        # Elle continue donc jusqu'à une page seule, même si le lot parent a déjà échoué.
        if self.config.batching.split_on_failure and len(batch.page_numbers) > 1:
            split = self.planner.split(batch)
            return list(split) if split else []
        if batch.attempt >= self.config.batching.retry_limit:
            return []
        return [
            PageBatch(
                page_numbers=batch.page_numbers,
                estimated_context_units=batch.estimated_context_units,
                attempt=batch.attempt + 1,
                parent_batch_id=batch.id,
            )
        ]

    @staticmethod
    def _write_json(path: Path, payload: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        temporary.replace(path)

    def _checkpoint(self, artifact_dir: Path, ledger: IngestionLedger) -> None:
        ledger.touch()
        self._write_json(artifact_dir / "ingestion_ledger.json", ledger.model_dump(mode="json"))

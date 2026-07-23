from __future__ import annotations

import json
import shutil
from pathlib import Path
from uuid import uuid4

from control_tower.brain.orchestrator import Brain
from control_tower.domain.models import AtomicChunk, ModuleResult, PolicyEffect, ResultStatus
from control_tower.ingestion.atomizer import AtomicChunker
from control_tower.observability.events import event
from control_tower.ocr.models import ExtractedPage
from control_tower.ocr.router import DocumentExtractor
from control_tower.optimization.consolidator import Consolidator
from control_tower.policy.checker import PolicyChecker
from control_tower.processing.executor import LongPDFProcessor
from control_tower.processing.models import LongPDFResult, PageAnalysis, VisualAsset
from control_tower.project.workspace import WorkspaceManager
from control_tower.semantics.kant_glove import KantGloveAnalyzer
from control_tower.semantics.maieutic import MaieuticAnalyzer
from control_tower.semantics.pseudocode import PseudocodeAnalyzer
from control_tower.storage.sqlite import SQLiteStore


class IngestionPipeline:
    def __init__(
        self,
        workspace: WorkspaceManager,
        extractor: DocumentExtractor | None = None,
    ) -> None:
        self.workspace = workspace
        self.policy = PolicyChecker(workspace)
        self.extractor = extractor or DocumentExtractor()
        self.brain = Brain()

    def ingest(self, project_id: str, source: Path, allow_review: bool = False) -> ModuleResult:
        config = self.workspace.load_config(project_id)
        plan = self.brain.plan_ingestion(project_id)
        self.workspace.append_event(
            project_id,
            event("brain.plan.created", plan=plan.model_dump(mode="json")),
        )

        decision = self.policy.check_ingestion(project_id, source, config)
        self.workspace.append_event(
            project_id,
            event(
                "policy.decision",
                action="ingest",
                source=str(source),
                decision=decision.model_dump(),
            ),
        )

        if decision.effect == PolicyEffect.DENY:
            return ModuleResult(
                status=ResultStatus.BLOCKED,
                module="ingestion",
                errors=[decision.reason],
                data={"policy": decision.model_dump(), "execution_plan": plan.model_dump()},
            )
        if decision.effect == PolicyEffect.REVIEW and not allow_review:
            return ModuleResult(
                status=ResultStatus.BLOCKED,
                module="ingestion",
                errors=[decision.reason],
                data={"policy": decision.model_dump(), "execution_plan": plan.model_dump()},
            )

        project_path = self.workspace.path_for(project_id)
        document_id = str(uuid4())
        copied = project_path / "documents" / f"{document_id}{source.suffix.lower()}"
        shutil.copy2(source, copied)
        artifact_dir = project_path / "artifacts" / document_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        long_pdf: LongPDFResult | None = None
        try:
            if copied.suffix.lower() == ".pdf" and config.batching.enabled:
                long_pdf = LongPDFProcessor(config).process(copied, document_id, artifact_dir)
                extraction = long_pdf.extraction
                self._merge_multimodal_text(extraction.pages, long_pdf.analyses)
            else:
                extraction = self.extractor.extract(copied, config.ocr)
        except (RuntimeError, ValueError, OSError) as exc:
            self.workspace.append_event(
                project_id,
                event(
                    "extraction.failed",
                    document_id=document_id,
                    source_name=source.name,
                    error=str(exc),
                ),
            )
            return ModuleResult(
                status=ResultStatus.ERROR,
                module="ingestion",
                errors=[str(exc)],
                data={
                    "project_id": project_id,
                    "document_id": document_id,
                    "stored_copy": str(copied),
                    "artifact_dir": str(artifact_dir),
                    "policy": decision.model_dump(),
                    "execution_plan": plan.model_dump(),
                },
            )

        extraction_json = artifact_dir / "extraction.json"
        extracted_text = artifact_dir / "extracted.txt"
        extraction_json.write_text(
            json.dumps(extraction.artifact_payload(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        extracted_text.write_text(extraction.text, encoding="utf-8")

        if long_pdf and not long_pdf.complete and config.batching.strict_completeness:
            summary = long_pdf.ledger.summary()
            self.workspace.append_event(
                project_id,
                event(
                    "ingestion.incomplete",
                    document_id=document_id,
                    source_name=source.name,
                    ledger=summary,
                ),
            )
            return ModuleResult(
                status=ResultStatus.ERROR,
                module="ingestion",
                errors=[
                    "PDF incomplet: aucun chunk n'a été indexé car le contrôle de complétude a échoué."
                ],
                warnings=extraction.warnings,
                data={
                    "project_id": project_id,
                    "document_id": document_id,
                    "stored_copy": str(copied),
                    "ledger": summary,
                    "artifacts": {
                        "artifact_dir": str(artifact_dir),
                        "ledger": str(artifact_dir / "ingestion_ledger.json"),
                        "extraction_json": str(extraction_json),
                        "extracted_text": str(extracted_text),
                    },
                },
            )

        chunker = AtomicChunker(
            max_chars=config.atomizer.max_chars,
            overlap_chars=config.atomizer.overlap_chars,
        )
        chunks: list[AtomicChunk] = []
        ordinal = 0
        analyses = long_pdf.analyses if long_pdf else {}
        assets = long_pdf.assets if long_pdf else []
        assets_by_page: dict[int, list[VisualAsset]] = {}
        for asset in assets:
            assets_by_page.setdefault(asset.page_number, []).append(asset)

        for page in extraction.pages:
            page_chunks = chunker.split(
                project_id,
                document_id,
                page.text,
                start_ordinal=ordinal,
                source_pages=[page.page_number],
                extraction_method=page.method.value,
            )
            analysis = analyses.get(page.page_number)
            raw_asset_ids = [asset.id for asset in assets_by_page.get(page.page_number, [])]
            page_chunks = [
                self._apply_page_analysis(
                    chunk,
                    analysis,
                    raw_asset_ids,
                    pseudocode_enabled=config.features.pseudocode,
                    maieutic_enabled=config.features.maieutic,
                    kant_enabled=config.features.kant_glove,
                )
                for chunk in page_chunks
            ]
            chunks.extend(page_chunks)
            ordinal += len(page_chunks)

        if not chunks:
            return ModuleResult(
                status=ResultStatus.ERROR,
                module="ingestion",
                errors=["L'extraction n'a produit aucun chunk exploitable."],
                warnings=extraction.warnings,
                data={
                    "project_id": project_id,
                    "document_id": document_id,
                    "stored_copy": str(copied),
                    "artifacts": {
                        "extraction_json": str(extraction_json),
                        "extracted_text": str(extracted_text),
                    },
                },
            )

        if config.features.pseudocode:
            analyzer = PseudocodeAnalyzer()
            chunks = [analyzer.enrich(chunk) for chunk in chunks]
        if config.features.maieutic:
            analyzer = MaieuticAnalyzer()
            chunks = [analyzer.enrich(chunk) for chunk in chunks]
        if config.features.kant_glove:
            analyzer = KantGloveAnalyzer()
            chunks = [analyzer.enrich(chunk) for chunk in chunks]

        consolidator = Consolidator(config=config.consolidation)
        chunks, assets, consolidation = consolidator.consolidate(chunks, assets)
        canonical_asset_ids = {
            asset.id: asset.canonical_asset_id or asset.id
            for asset in assets
        }
        chunks = [
            chunk.model_copy(
                update={
                    "visual_asset_ids": list(
                        dict.fromkeys(
                            canonical_asset_ids.get(asset_id, asset_id)
                            for asset_id in chunk.visual_asset_ids
                        )
                    )
                }
            )
            for chunk in chunks
        ]
        (artifact_dir / "consolidation.json").write_text(
            json.dumps(consolidation.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (artifact_dir / "visual_assets.json").write_text(
            json.dumps(
                [asset.model_dump(mode="json") for asset in assets],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        store = SQLiteStore(project_path / "state" / "knowledge.db")
        store.save_chunks(chunks)
        extraction_summary = {
            "pages": len(extraction.pages),
            "characters": extraction.character_count,
            "methods": extraction.methods,
            "warnings": extraction.warnings,
        }
        ledger_summary = long_pdf.ledger.summary() if long_pdf else None
        self.workspace.append_event(
            project_id,
            event(
                "ingestion.completed",
                document_id=document_id,
                source_name=source.name,
                chunk_count=len(chunks),
                canonical_chunk_count=consolidation.canonical_chunks,
                extraction=extraction_summary,
                ledger=ledger_summary,
                consolidation=consolidation.model_dump(mode="json"),
                active_features=config.features.model_dump(),
                atomizer=config.atomizer.model_dump(),
                ocr=config.ocr.model_dump(),
                batching=config.batching.model_dump(),
                vision=config.vision.model_dump(),
            ),
        )
        return ModuleResult(
            status=ResultStatus.OK,
            module="ingestion",
            data={
                "project_id": project_id,
                "document_id": document_id,
                "stored_copy": str(copied),
                "chunk_count": len(chunks),
                "canonical_chunk_count": consolidation.canonical_chunks,
                "extraction": extraction_summary,
                "ledger": ledger_summary,
                "consolidation": consolidation.model_dump(mode="json"),
                "artifacts": {
                    "artifact_dir": str(artifact_dir),
                    "extraction_json": str(extraction_json),
                    "extracted_text": str(extracted_text),
                    "ledger": str(artifact_dir / "ingestion_ledger.json") if long_pdf else None,
                    "page_analyses": str(artifact_dir / "page_analyses.json") if long_pdf else None,
                    "provider_report": str(artifact_dir / "provider_report.json")
                    if (long_pdf and (artifact_dir / "provider_report.json").exists()) else None,
                    "consolidation": str(artifact_dir / "consolidation.json"),
                    "visual_assets": str(artifact_dir / "visual_assets.json"),
                },
                "policy": decision.model_dump(),
                "execution_plan": plan.model_dump(),
                "active_config": {
                    "atomizer": config.atomizer.model_dump(),
                    "ocr": config.ocr.model_dump(),
                    "batching": config.batching.model_dump(),
                    "vision": config.vision.model_dump(),
                    "consolidation": config.consolidation.model_dump(),
                    "features": config.features.model_dump(),
                },
            },
            warnings=extraction.warnings + consolidation.warnings,
            metrics={
                "characters": extraction.character_count,
                "pages": len(extraction.pages),
                "chunks": len(chunks),
                "canonical_chunks": consolidation.canonical_chunks,
                "duplicate_chunks": len(chunks) - consolidation.canonical_chunks,
                "visual_assets": len(assets),
            },
        )

    @staticmethod
    def _merge_multimodal_text(
        pages: list[ExtractedPage],
        analyses: dict[int, PageAnalysis],
    ) -> None:
        for page in pages:
            analysis = analyses.get(page.page_number)
            if analysis is None or analysis.provider == "local":
                continue
            supplements: list[str] = []
            normalized_values = [" ".join(page.text.casefold().split())]
            for value in (analysis.extracted_text, analysis.handwriting_text):
                value = value.strip()
                normalized = " ".join(value.casefold().split())
                if not value:
                    continue
                if any(
                    normalized in existing or existing in normalized
                    for existing in normalized_values
                    if existing
                ):
                    continue
                supplements.append(value)
                normalized_values.append(normalized)
            if supplements:
                page.text = "\n\n".join([page.text.strip(), *supplements]).strip()
                page.supplemental_methods.append("multimodal_vision")

    @staticmethod
    def _apply_page_analysis(
        chunk: AtomicChunk,
        analysis: PageAnalysis | None,
        visual_asset_ids: list[str],
        *,
        pseudocode_enabled: bool,
        maieutic_enabled: bool,
        kant_enabled: bool,
    ) -> AtomicChunk:
        if analysis is None:
            return chunk.model_copy(update={"visual_asset_ids": visual_asset_ids})
        return chunk.model_copy(
            update={
                "concepts": analysis.concepts,
                "pseudocode": analysis.pseudocode if pseudocode_enabled else [],
                "questions": analysis.maieutic_questions if maieutic_enabled else [],
                "tensions": analysis.kant_tensions if kant_enabled else [],
                "visual_asset_ids": visual_asset_ids,
                "tags": list(
                    dict.fromkeys(
                        [
                            *chunk.tags,
                            f"vision_provider:{analysis.provider}",
                            *(f"symbol:{symbol}" for symbol in analysis.symbols[:12]),
                        ]
                    )
                ),
            }
        )

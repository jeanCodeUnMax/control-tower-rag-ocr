from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

from control_tower.brain.orchestrator import Brain
from control_tower.config import parse_cli_value
from control_tower.hydration.engine import HydrationEngine
from control_tower.ingestion.pipeline import IngestionPipeline
from control_tower.ocr.pdf import PDFOCRProvider
from control_tower.ocr.router import DocumentExtractor
from control_tower.processing.batching import AdaptiveBatchPlanner
from control_tower.processing.rendering import render_pdf_pages
from control_tower.processing.routing import plan_routes, route_page
from control_tower.processing.vision import build_vision_analyzer
from control_tower.project.workspace import WorkspaceManager
from control_tower.registry.registry import build_default_registry
from control_tower.storage.sqlite import SQLiteStore


class ControlTowerService:
    def __init__(
        self,
        workspace_root: Path | None = None,
        extractor: DocumentExtractor | None = None,
    ) -> None:
        self.workspace = WorkspaceManager(workspace_root)
        self.ingestion = IngestionPipeline(self.workspace, extractor=extractor)
        self.hydrator = HydrationEngine()
        self.brain = Brain()
        self.registry = build_default_registry()

    def init_project(self, project_id: str, name: str | None = None) -> dict:
        project = self.workspace.create(project_id, name)
        return {
            **project.model_dump(mode="json"),
            "config_path": str(self.workspace.config_path(project_id)),
            "config": self.workspace.load_config(project_id).model_dump(mode="json"),
        }

    def ingest(self, project_id: str, source: Path, allow_review: bool = False) -> dict:
        self.workspace.require(project_id)
        result = self.ingestion.ingest(project_id, source, allow_review=allow_review).model_dump(mode="json")
        
        # Si une ancienne version a été écrasée, on purge ses vecteurs
        replaced_document_id = result.get("data", {}).get("replaced_document_id")
        if replaced_document_id:
            import logging
            logger = logging.getLogger(__name__)
            from control_tower.storage.vector import QdrantVectorStore, ZvecRestStore
            
            # Nom de collection par défaut (souvent knowledge ou project_id)
            # Dans vectorize_project, la collection est project_id
            collection_name = project_id
            
            for store_cls in (QdrantVectorStore, ZvecRestStore):
                try:
                    vs = store_cls(path=str(self.workspace.path_for(project_id) / "state" / "qdrant_db")) if store_cls is QdrantVectorStore else store_cls()
                    vs.delete_by_document_id(collection_name, replaced_document_id)
                except Exception as e:
                    logger.warning(f"Impossible de purger l'ancienne version sur {store_cls.__name__} : {e}")
                    
        # Si l'ingestion est un succès, on déclenche les phases finales automatiques
        if result.get("status") == "ok":
            import logging
            logger = logging.getLogger(__name__)
            
            # 1. Vectorisation automatique (Qdrant Local par défaut dans ce mode)
            try:
                logger.info("Démarrage de la vectorisation automatique...")
                vector_res = self.vectorize_project(project_id, database="qdrant_local")
                result["vectorization"] = vector_res
            except Exception as e:
                logger.error(f"Erreur vectorisation: {e}")
                result["vectorization"] = {"status": "error", "message": str(e)}
                
            # 2. Test final dans l'Arène
            try:
                logger.info("Lancement du test QA automatique dans l'Arène...")
                qa_res = self.ask_project(
                    project_id, 
                    f"Fais une très brève synthèse des concepts clés abordés dans {source.name}.",
                    database="qdrant_local"
                )
                result["auto_qa_test"] = qa_res
            except Exception as e:
                logger.error(f"Erreur QA test: {e}")
                result["auto_qa_test"] = {"status": "error", "message": str(e)}
                
        return result

    def consolidate_project(self, project_id: str) -> dict:
        import json
        from control_tower.optimization.consolidator import Consolidator
        from control_tower.processing.models import VisualAsset
        
        self.workspace.require(project_id)
        config = self.workspace.load_config(project_id)
        store = SQLiteStore(self.workspace.path_for(project_id) / "state" / "knowledge.db")
        
        all_chunks = store.all_chunks()
        
        artifacts_dir = self.workspace.path_for(project_id) / "artifacts"
        all_assets = []
        asset_files = list(artifacts_dir.glob("*/visual_assets.json"))
        for asset_file in asset_files:
            try:
                data = json.loads(asset_file.read_text(encoding="utf-8"))
                for asset_data in data:
                    all_assets.append(VisualAsset.model_validate(asset_data))
            except Exception:
                pass
                
        consolidator = Consolidator(config=config.consolidation)
        updated_chunks, updated_assets, stats = consolidator.consolidate(all_chunks, all_assets)
        
        store.replace_all_chunks(updated_chunks)
        
        from collections import defaultdict
        assets_by_doc = defaultdict(list)
        for asset in updated_assets:
            assets_by_doc[asset.document_id].append(asset)
            
        for doc_id, doc_assets in assets_by_doc.items():
            asset_file = artifacts_dir / doc_id / "visual_assets.json"
            if asset_file.exists():
                asset_file.write_text(json.dumps([a.model_dump(mode="json") for a in doc_assets], ensure_ascii=False, indent=2))
                
        # Supprimer les doublons des bases vectorielles
        from control_tower.domain.models import DuplicateKind
        from control_tower.storage.vector import QdrantVectorStore, ZvecRestStore
        
        duplicate_ids = [
            c.id for c in updated_chunks 
            if c.duplicate_kind != DuplicateKind.CANONICAL and c.canonical_id and c.canonical_id != c.id
        ]
        if duplicate_ids:
            for store_cls in (QdrantVectorStore, ZvecRestStore):
                try:
                    vs = store_cls(url="local") if store_cls is QdrantVectorStore else store_cls()
                    vs.delete(project_id, duplicate_ids)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Impossible de supprimer les doublons sur {store_cls.__name__} : {e}")
                
        return {
            "project_id": project_id,
            "consolidation_stats": stats
        }

    def query(self, project_id: str, text: str, top_k: int | None = None) -> dict:
        self.workspace.require(project_id)
        config = self.workspace.load_config(project_id)
        store = SQLiteStore(self.workspace.path_for(project_id) / "state" / "knowledge.db")
        effective_top_k = top_k if top_k is not None else config.retrieval.top_k
        hits = store.search(
            text,
            top_k=effective_top_k,
            canonical_only=config.retrieval.canonical_only,
        )
        return {
            "project_id": project_id,
            "query": text,
            "retrieval": {
                "engine": "lexical",
                "top_k": effective_top_k,
                "canonical_only": config.retrieval.canonical_only,
            },
            "hits": [hit.model_dump(mode="json") for hit in hits],
            "hydrated": self.hydrator.hydrate(
                hits, budget_chars=config.retrieval.hydration_budget_chars
            ),
        }

    def show_config(self, project_id: str) -> dict:
        return {
            "project_id": project_id,
            "path": str(self.workspace.config_path(project_id)),
            "config": self.workspace.load_config(project_id).model_dump(mode="json"),
        }

    def set_config(self, project_id: str, key: str, raw_value: str) -> dict:
        value: Any = parse_cli_value(raw_value)
        config = self.workspace.update_config(project_id, key, value)
        return {
            "project_id": project_id,
            "updated": {"key": key, "value": value},
            "config": config.model_dump(mode="json"),
        }


    def plan_document(self, project_id: str, source: Path) -> dict:
        """Préflight sans appel cloud: pages, lots, routes et coût minimal estimé."""
        self.workspace.require(project_id)
        if source.suffix.lower() != ".pdf":
            raise ValueError("Le préflight adaptatif est actuellement réservé aux PDF.")
        config = self.workspace.load_config(project_id)
        provider = PDFOCRProvider()
        profiles = provider.profile(source, config.ocr, config.batching)
        batches = AdaptiveBatchPlanner(config.batching).plan(profiles)
        routes = plan_routes(profiles, config.vision)
        return {
            "project_id": project_id,
            "source": str(source),
            "pdf_pages": len(profiles),
            "batch_count": len(batches),
            "batch_sizes": [len(batch.page_numbers) for batch in batches],
            "batch_plan": [batch.model_dump(mode="json") for batch in batches],
            "vision_plan": routes,
            "recommendation": self._profile_recommendation(routes),
        }

    def benchmark_vision(
        self,
        project_id: str,
        source: Path,
        max_pages: int = 12,
    ) -> dict:
        """Exécute le provider configuré sur un petit échantillon représentatif."""
        self.workspace.require(project_id)
        if source.suffix.lower() != ".pdf":
            raise ValueError("Le benchmark vision est actuellement réservé aux PDF.")
        if max_pages < 1 or max_pages > 50:
            raise ValueError("max_pages doit être compris entre 1 et 50.")
        config = self.workspace.load_config(project_id)
        pdf_provider = PDFOCRProvider()
        profiles = pdf_provider.profile(source, config.ocr, config.batching)
        selected = self._sample_profiles(profiles, max_pages)
        selected_numbers = [profile.page_number for profile in selected]
        extraction = pdf_provider.extract_pages(source, config.ocr, selected_numbers)
        extraction_by_page = {page.page_number: page for page in extraction.pages}
        cloud_numbers = [
            profile.page_number
            for profile in selected
            if route_page(profile, config.vision) == "cloud"
        ]
        benchmark_id = str(uuid4())
        root = self.workspace.path_for(project_id) / "benchmarks" / benchmark_id
        rendered_by_page = {}
        if cloud_numbers:
            rendered_by_page = {
                page.page_number: page.model_copy(
                    update={"native_text": extraction_by_page[page.page_number].text}
                )
                for page in render_pdf_pages(
                    source,
                    cloud_numbers,
                    root / "renders",
                    dpi=config.vision.render_dpi,
                    profiles={profile.page_number: profile for profile in profiles},
                )
            }
        from control_tower.processing.models import RenderedPage

        pages = [
            rendered_by_page.get(
                profile.page_number,
                RenderedPage(
                    page_number=profile.page_number,
                    image_path=source,
                    native_text=extraction_by_page[profile.page_number].text,
                    image_count=profile.image_count,
                    drawing_count=profile.drawing_count,
                ),
            )
            for profile in selected
        ]
        analyzer = build_vision_analyzer(config.vision)
        started = perf_counter()
        analyses = analyzer.analyze_batch(
            pages,
            {profile.page_number: profile for profile in selected},
        )
        elapsed = perf_counter() - started
        provider_report = getattr(analyzer, "report", lambda: {})()
        result = {
            "benchmark_id": benchmark_id,
            "project_id": project_id,
            "source": str(source),
            "profile": config.vision.profile,
            "sampled_pages": selected_numbers,
            "elapsed_seconds": round(elapsed, 3),
            "pages_per_minute": round(len(selected) / elapsed * 60, 2) if elapsed else None,
            "estimated_800_page_minutes": round(800 / (len(selected) / elapsed) / 60, 2)
            if elapsed else None,
            "analyses": [analysis.model_dump(mode="json") for analysis in analyses],
            "provider_report": provider_report,
        }
        root.mkdir(parents=True, exist_ok=True)
        import json

        (root / "benchmark.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        result["artifact"] = str(root / "benchmark.json")
        return result

    def enrich_document(
        self,
        project_id: str,
        document_id: str,
        profile: str = "cloud_turbo",
    ) -> dict:
        """Reprend les pages différées et reconstruit le même document sans duplication."""
        if profile not in {"balanced", "cloud_turbo", "night_deep"}:
            raise ValueError("Le profil d'enrichissement doit être balanced, cloud_turbo ou night_deep.")
        self.workspace.require(project_id)
        project_path = self.workspace.path_for(project_id)
        artifact_dir = project_path / "artifacts" / document_id
        extraction_path = artifact_dir / "extraction.json"
        profiles_path = artifact_dir / "page_profiles.json"
        analyses_path = artifact_dir / "page_analyses.json"
        if not extraction_path.exists() or not profiles_path.exists():
            raise ValueError(f"Document PDF inconnu ou artefacts incomplets: {document_id}")

        import json
        from control_tower.domain.models import AtomicChunk
        from control_tower.ingestion.atomizer import AtomicChunker
        from control_tower.ocr.models import ExtractionResult
        from control_tower.optimization.consolidator import Consolidator
        from control_tower.processing.models import PageAnalysis, PageProfile, RenderedPage, VisualAsset
        from control_tower.semantics.kant_glove import KantGloveAnalyzer
        from control_tower.semantics.maieutic import MaieuticAnalyzer
        from control_tower.semantics.pseudocode import PseudocodeAnalyzer

        extraction = ExtractionResult.model_validate_json(extraction_path.read_text(encoding="utf-8"))
        source = Path(extraction.source_path)
        if not source.exists():
            raise ValueError(f"Copie source introuvable: {source}")
        profiles = [
            PageProfile.model_validate(item)
            for item in json.loads(profiles_path.read_text(encoding="utf-8"))
        ]
        profile_map = {item.page_number: item for item in profiles}
        previous_analyses_raw = (
            json.loads(analyses_path.read_text(encoding="utf-8"))
            if analyses_path.exists()
            else {}
        )
        analyses = {
            int(number): PageAnalysis.model_validate(value)
            for number, value in previous_analyses_raw.items()
        }
        selected_numbers = sorted(
            number
            for number, analysis in analyses.items()
            if analysis.needs_multimodal_review
        )
        if not selected_numbers:
            provider_report_path = artifact_dir / "provider_report.json"
            if provider_report_path.exists():
                report = json.loads(provider_report_path.read_text(encoding="utf-8"))
                selected_numbers = sorted(report.get("deferred_pages", []))
        if not selected_numbers:
            return {
                "project_id": project_id,
                "document_id": document_id,
                "status": "nothing_to_enrich",
                "enriched_pages": [],
            }

        config = self.workspace.load_config(project_id).model_copy(deep=True)
        config.vision.provider = "router"
        config.vision.profile = profile
        analyzer = build_vision_analyzer(config.vision)
        extraction_by_page = {page.page_number: page for page in extraction.pages}
        new_analyses: dict[int, PageAnalysis] = {}
        group_size = max(1, min(config.vision.max_workers, 20))
        for offset in range(0, len(selected_numbers), group_size):
            group = selected_numbers[offset : offset + group_size]
            rendered = render_pdf_pages(
                source,
                group,
                artifact_dir / "renders_enrichment",
                dpi=config.vision.render_dpi,
                profiles=profile_map,
            )
            pages = [
                page.model_copy(
                    update={"native_text": extraction_by_page[page.page_number].text}
                )
                for page in rendered
            ]
            batch_analyses = analyzer.analyze_batch(
                pages,
                {number: profile_map[number] for number in group},
            )
            new_analyses.update({item.page_number: item for item in batch_analyses})

        analyses.update(new_analyses)
        IngestionPipeline._merge_multimodal_text(extraction.pages, new_analyses)
        extraction_path.write_text(extraction.model_dump_json(indent=2), encoding="utf-8")
        (artifact_dir / "extracted.txt").write_text(extraction.text, encoding="utf-8")
        analyses_path.write_text(
            json.dumps(
                {str(number): item.model_dump(mode="json") for number, item in sorted(analyses.items())},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        for number, analysis in new_analyses.items():
            page_path = artifact_dir / "pages" / f"page_{number:05d}.json"
            if page_path.exists():
                payload = json.loads(page_path.read_text(encoding="utf-8"))
                payload["analysis"] = analysis.model_dump(mode="json")
                page_path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
                )

        assets_path = artifact_dir / "visual_assets.json"
        assets = (
            [VisualAsset.model_validate(item) for item in json.loads(assets_path.read_text(encoding="utf-8"))]
            if assets_path.exists()
            else []
        )
        assets_by_page: dict[int, list[VisualAsset]] = {}
        for asset in assets:
            assets_by_page.setdefault(asset.page_number, []).append(asset)

        chunker = AtomicChunker(
            max_chars=config.atomizer.max_chars,
            overlap_chars=config.atomizer.overlap_chars,
        )
        chunks: list[AtomicChunk] = []
        ordinal = 0
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
            raw_asset_ids = [item.id for item in assets_by_page.get(page.page_number, [])]
            page_chunks = [
                self.ingestion._apply_page_analysis(
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

        if config.features.pseudocode:
            pseudocode = PseudocodeAnalyzer()
            chunks = [pseudocode.enrich(chunk) for chunk in chunks]
        if config.features.maieutic:
            maieutic = MaieuticAnalyzer()
            chunks = [maieutic.enrich(chunk) for chunk in chunks]
        if config.features.kant_glove:
            kant = KantGloveAnalyzer()
            chunks = [kant.enrich(chunk) for chunk in chunks]

        chunks, assets, consolidation = Consolidator(config=config.consolidation).consolidate(
            chunks, assets
        )
        canonical_asset_ids = {asset.id: asset.canonical_asset_id or asset.id for asset in assets}
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
        store = SQLiteStore(project_path / "state" / "knowledge.db")
        store.replace_document_chunks(document_id, chunks)
        (artifact_dir / "consolidation.json").write_text(
            consolidation.model_dump_json(indent=2), encoding="utf-8"
        )
        assets_path.write_text(
            json.dumps([item.model_dump(mode="json") for item in assets], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report = getattr(analyzer, "report", lambda: {})()
        report["enrichment_profile"] = profile
        report["enriched_pages"] = selected_numbers
        report["remaining_review_pages"] = sorted(
            number for number, item in analyses.items() if item.needs_multimodal_review
        )
        (artifact_dir / "provider_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self.workspace.append_event(
            project_id,
            {
                "type": "document.enriched",
                "document_id": document_id,
                "profile": profile,
                "pages": selected_numbers,
                "canonical_chunks": consolidation.canonical_chunks,
            },
        )
        return {
            "project_id": project_id,
            "document_id": document_id,
            "status": "enriched",
            "profile": profile,
            "enriched_pages": selected_numbers,
            "remaining_review_pages": report["remaining_review_pages"],
            "chunk_count": len(chunks),
            "canonical_chunk_count": consolidation.canonical_chunks,
            "provider_report": report,
            "artifacts": {
                "page_analyses": str(analyses_path),
                "provider_report": str(artifact_dir / "provider_report.json"),
                "consolidation": str(artifact_dir / "consolidation.json"),
            },
        }

    @staticmethod
    def _sample_profiles(profiles, maximum: int):
        if len(profiles) <= maximum:
            return profiles
        complex_profiles = [
            profile for profile in profiles
            if profile.requires_visual_analysis or profile.requires_ocr
        ]
        selected = complex_profiles[: maximum // 2]
        selected_numbers = {profile.page_number for profile in selected}
        remaining = [profile for profile in profiles if profile.page_number not in selected_numbers]
        slots = maximum - len(selected)
        if slots and remaining:
            if slots == 1:
                selected.append(remaining[len(remaining) // 2])
            else:
                indexes = [
                    round(index * (len(remaining) - 1) / (slots - 1))
                    for index in range(slots)
                ]
                selected.extend(remaining[index] for index in indexes)
        unique = {item.page_number: item for item in selected}
        return sorted(unique.values(), key=lambda item: item.page_number)[:maximum]

    @staticmethod
    def _profile_recommendation(routes: dict) -> str:
        counts = routes["counts"]
        if counts["cloud"] == 0 and counts["deferred"] == 0:
            return "local_fast suffit: aucune page complexe détectée."
        if counts["deferred"]:
            return (
                "Le document sera disponible rapidement, puis les pages différées pourront "
                "être enrichies pendant la nuit."
            )
        ratio = counts["cloud"] / max(1, routes["page_count"])
        if ratio < 0.25:
            return "balanced: moins de 25 % des pages nécessitent le cloud."
        return "cloud_turbo conseillé: forte densité de pages complexes."


    def inspect_document(self, project_id: str, document_id: str) -> dict:
        self.workspace.require(project_id)
        project_path = self.workspace.path_for(project_id)
        artifact_path = project_path / "artifacts" / document_id / "extraction.json"
        if not artifact_path.exists():
            raise ValueError(f"Document inconnu ou artefact absent: {document_id}")
        import json

        store = SQLiteStore(project_path / "state" / "knowledge.db")
        artifact_dir = artifact_path.parent
        optional_artifacts = {}
        for name in (
            "ingestion_ledger.json",
            "page_profiles.json",
            "batch_plan.json",
            "page_analyses.json",
            "consolidation.json",
            "visual_assets.json",
            "provider_report.json",
        ):
            candidate = artifact_dir / name
            if candidate.exists():
                optional_artifacts[name] = json.loads(candidate.read_text(encoding="utf-8"))
        return {
            "project_id": project_id,
            "document_id": document_id,
            "artifact_dir": str(artifact_dir),
            "extraction_artifact": str(artifact_path),
            "extraction": json.loads(artifact_path.read_text(encoding="utf-8")),
            "processing": optional_artifacts,
            "chunks": [
                chunk.model_dump(mode="json")
                for chunk in store.chunks_for_document(document_id)
            ],
        }

    def inspect_project(self, project_id: str) -> dict:
        project = self.workspace.require(project_id)
        config = self.workspace.load_config(project_id)
        project_path = self.workspace.path_for(project_id)
        store = SQLiteStore(project_path / "state" / "knowledge.db")
        return {
            "project": project.model_dump(mode="json"),
            "workspace": str(project_path),
            "config_path": str(self.workspace.config_path(project_id)),
            "active_config": config.model_dump(mode="json"),
            "ingestion_plan": self.brain.plan_ingestion(project_id).model_dump(mode="json"),
            "store": store.stats(),
            "capabilities": [capability.__dict__ for capability in self.registry.list()],
        }

    def vectorize_project(self, project_id: str, database: str = "zvec") -> dict:
        """Génère les embeddings et les insère dans le Vector Store."""
        self.workspace.require(project_id)
        config = self.workspace.load_config(project_id)
        project_path = self.workspace.path_for(project_id)
        
        from control_tower.semantics.embeddings import get_embedding_provider
        from control_tower.storage.vector import QdrantVectorStore, ZvecRestStore
        
        # Initialiser le provider d'embeddings
        provider_type = "zvec" if database == "zvec" else config.embeddings.provider
        embedder = get_embedding_provider(
            provider_type=provider_type,
            model_name=config.embeddings.model
        )
        
        # Initialiser le store vectoriel (Anti-Fragile)
        if database == "zvec":
            vector_store = ZvecRestStore(url="http://localhost:8001")
        elif database == "qdrant_local":
            vector_store = QdrantVectorStore(path=str(project_path / "state" / "qdrant_db"), url=config.vector_store.url)
        else:
            raise ValueError(f"Base de données non supportée: {database}")
            
        store = SQLiteStore(project_path / "state" / "knowledge.db")
        
        # Récupérer tous les chunks du SQLite
        chunks = store.all_chunks()
        
        if not chunks:
            return {"status": "no_chunks_found"}
            
        # Pour faire simple dans la V1 : on re-vectorise tout
        texts_to_embed = [chunk.text for chunk in chunks]
        
        # TODO: Batching selon les limites de l'API/Provider
        vectors = embedder.embed_batch(texts_to_embed)
        
        # S'assurer que la collection existe avec la bonne dimension
        vector_store.init_collection(config.vector_store.collection_name, embedder.dimension)
        
        upserted_count = 0
        for chunk, vector in zip(chunks, vectors):
            payload = chunk.model_dump(mode="json")
            vector_store.upsert(
                collection_name=config.vector_store.collection_name,
                point_id=chunk.id,
                vector=vector,
                payload=payload
            )
            upserted_count += 1
            
        return {
            "project_id": project_id,
            "status": "vectorized",
            "chunks_processed": len(chunks),
            "vectors_upserted": upserted_count,
            "dimension": embedder.dimension,
            "vector_store": config.vector_store.engine
        }

    def ask_project(self, project_id: str, question: str, top_k: int = 5, database: str = "zvec", paradigm: str = "executive") -> dict:
        """Pose une question au RAG du projet."""
        self.workspace.require(project_id)
        config = self.workspace.load_config(project_id)
        
        from control_tower.semantics.embeddings import get_embedding_provider
        from control_tower.storage.vector import QdrantVectorStore, ZvecRestStore
        from control_tower.generation.llm import get_llm_provider
        from control_tower.retrieval.rag import RAGEngine
        
        # Initialiser les briques
        provider_type = "zvec" if database == "zvec" else config.embeddings.provider
        embedder = get_embedding_provider(
            provider_type=provider_type,
            model_name=config.embeddings.model
        )
        
        project_path = self.workspace.path_for(project_id)
        if database == "zvec":
            vector_store = ZvecRestStore(url="http://localhost:8001")
        elif database == "qdrant_local":
            vector_store = QdrantVectorStore(path=str(project_path / "state" / "qdrant_db"), url=config.vector_store.url)
        else:
            raise ValueError(f"Base de données non supportée: {database}")
            
        llm = get_llm_provider(
            provider_type=config.llm.provider,
            config_obj=config.llm,
            model_name=config.llm.model,
            api_key_env=config.llm.api_key_env,
            temperature=0.1 if paradigm == "executive" else config.llm.temperature
        )
        
        rag = RAGEngine(
            vector_store=vector_store,
            embedder=embedder,
            llm=llm,
            collection_name=config.vector_store.collection_name
        )
        
        return rag.ask(question=question, top_k=top_k, paradigm=paradigm)

    def compare_llms(self, project_id: str, question: str, top_k: int = 5) -> dict:
        """Compare les réponses de plusieurs LLMs en parallèle pour la même question."""
        self.workspace.require(project_id)
        config = self.workspace.load_config(project_id)
        
        from control_tower.semantics.embeddings import get_embedding_provider
        from control_tower.storage.vector import QdrantVectorStore
        from control_tower.generation.llm import get_llm_provider
        import concurrent.futures
        import time
        
        # 1. Obtenir le contexte UNE SEULE FOIS
        embedder = get_embedding_provider(
            provider_type=config.embeddings.provider,
            model_name=config.embeddings.model
        )
        
        project_path = self.workspace.path_for(project_id)
        if config.vector_store.engine == "qdrant":
            vector_store = QdrantVectorStore(path=str(project_path / "state" / "qdrant_db"), url=config.vector_store.url)
        else:
            raise ValueError(f"Moteur vectoriel non supporté: {config.vector_store.engine}")
            
        # Recherche
        query_vector = embedder.embed_text(question)
        results = vector_store.search(
            collection_name=config.vector_store.collection_name,
            query_vector=query_vector,
            limit=top_k,
        )

        sources = []
        context_parts = []
        if results:
            for i, hit in enumerate(results, 1):
                text = hit.get("text", "")
                doc_id = hit.get("document_id", "Inconnu")
                score = hit.get("score", 0.0)
                context_parts.append(f"--- Source {i} (Document: {doc_id}) ---\n{text}\n")
                sources.append({"document_id": doc_id, "score": score, "text_snippet": text[:100]})

        context_text = "\n".join(context_parts)
        
        system_prompt = (
            "Tu es 'Control Tower', un assistant IA expert en analyse documentaire. "
            "Ton rôle est de répondre aux questions de l'utilisateur de manière précise, "
            "en te basant EXCLUSIVEMENT sur les documents fournis dans le contexte ci-dessous.\n\n"
            "RÈGLES IMPORTANTES :\n"
            "- Si la réponse ne se trouve pas dans le contexte, dis-le clairement. N'invente rien.\n"
            "- Sois concis et direct."
        )

        user_prompt = f"CONTEXTE RÉCUPÉRÉ DES DOCUMENTS :\n{context_text}\n\nQUESTION DE L'UTILISATEUR :\n{question}"

        # 2. Lancer les LLMs en parallèle
        comparisons = []
        
        def call_llm(prov_config):
            start_time = time.time()
            try:
                llm = get_llm_provider(
                    provider_type=prov_config.kind,
                    config_obj=config.llm,
                    model_name=prov_config.model,
                    api_key_env=prov_config.api_key_env,
                    temperature=config.llm.temperature
                )
                answer = llm.generate(prompt=user_prompt, system_prompt=system_prompt)
                elapsed = time.time() - start_time
                return {
                    "name": prov_config.name,
                    "model": prov_config.model,
                    "answer": answer,
                    "time": elapsed,
                    "error": None
                }
            except Exception as e:
                elapsed = time.time() - start_time
                return {
                    "name": prov_config.name,
                    "model": prov_config.model,
                    "answer": None,
                    "time": elapsed,
                    "error": str(e)
                }

        # Extraire la liste des fournisseurs activés
        providers_to_test = [p for p in config.llm.providers if p.enabled]
        if not providers_to_test:
            # Si aucun n'est explicitement activé, on les teste tous
            providers_to_test = config.llm.providers
            if not providers_to_test:
                raise ValueError("Aucun fournisseur défini dans la configuration du projet.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(providers_to_test)) as executor:
            futures = [executor.submit(call_llm, p) for p in providers_to_test]
            for future in concurrent.futures.as_completed(futures):
                comparisons.append(future.result())

        return {
            "project_id": project_id,
            "question": question,
            "sources": sources,
            "comparisons": comparisons
        }

    def synthesize_llms(self, project_id: str, question: str, output_file: str = "synthese-ai-grouped.md", top_k: int = 5, use_web_search: bool = False, paradigm: str = "executive") -> dict:
        """Fait générer des réponses en parallèle puis utilise Mistral pour créer une méga-synthèse selon un paradigme donné."""
        import os
        from control_tower.generation.llm import get_llm_provider
        from control_tower.generation.paradigms import COGNITIVE_PARADIGMS
        
        # 1. Obtenir les comparaisons (Phase 1)
        compare_result = self.compare_llms(project_id, question, top_k)
        comparisons = compare_result.get("comparisons", [])
        
        # 2. Filtrer les réponses valides
        valid_answers = [c for c in comparisons if c.get("answer") and not c.get("error")]
        
        if not valid_answers:
            raise ValueError("Aucun LLM n'a réussi à générer une réponse valide pour la synthèse.")
            
        # 3. Construire le prompt de synthèse
        drafts_text = ""
        for i, ans in enumerate(valid_answers, 1):
            drafts_text += f"\n### Brouillon {i} (par {ans['name']} - {ans['model']}) :\n{ans['answer']}\n"
            
        # NOUVEAU : Option de recherche Web (DDGS)
        web_context_text = ""
        web_sources_count = 0
        if use_web_search:
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = list(ddgs.text(question, max_results=3, safesearch="moderate"))
                    if results:
                        web_sources_count = len(results)
                        web_context_text = "\n\n### INFORMATIONS TROUVÉES SUR LE WEB EN TEMPS RÉEL :\n"
                        for r in results:
                            web_context_text += f"- **[{r['title']}]({r['href']})** : {r['body']}\n"
            except ImportError:
                import logging
                logging.getLogger(__name__).warning("duckduckgo-search n'est pas installé. Recherche web ignorée.")
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Erreur lors de la recherche web: {e}")
                
        # 4. Sélectionner le prompt système selon le paradigme choisi
        if paradigm not in COGNITIVE_PARADIGMS:
            import logging
            logging.getLogger(__name__).warning(f"Paradigme '{paradigm}' inconnu. Utilisation de 'executive' par défaut.")
            paradigm = "executive"
            
        system_prompt = COGNITIVE_PARADIGMS[paradigm]
        
        user_prompt = (
            f"Voici la question originelle de l'utilisateur :\n{question}\n\n"
            f"Voici les brouillons générés par différentes intelligences artificielles (basés sur le RAG interne) :\n{drafts_text}\n"
        )
        if web_context_text:
            user_prompt += web_context_text
            
        user_prompt += "\n\nRédige maintenant ta réponse finale au format Markdown, en appliquant strictement ton paradigme."
        
        # 4. Trouver la config du Synthétiseur (Mistral par défaut, sinon Ollama)
        config = self.workspace.load_config(project_id)
        
        mistral_config = next((p for p in config.llm.providers if p.kind == "mistral"), None)
        has_mistral_key = bool(os.getenv("MISTRAL_API_KEY"))
        
        if mistral_config and has_mistral_key:
            synth_config = mistral_config
        else:
            # Fallback sur ollama
            synth_config = next((p for p in config.llm.providers if p.kind == "ollama"), None)
            if not synth_config:
                synth_config = next((p for p in config.llm.providers if p.enabled), None)
            if not synth_config:
                synth_config = config.llm.providers[0] if config.llm.providers else None
                
        if not synth_config:
            raise ValueError("Impossible de trouver un modèle pour réaliser la synthèse.")
            
        # 5. Appeler le synthétiseur avec la température à presque 0 pour brider la créativité
        llm = get_llm_provider(
            provider_type=synth_config.kind,
            config_obj=config.llm,
            model_name=synth_config.model,
            api_key_env=synth_config.api_key_env,
            temperature=0.1 # <--- STRICT GROUNDING : On bride la créativité au maximum
        )
        
        final_answer = llm.generate(prompt=user_prompt, system_prompt=system_prompt)
        
        # 6. Sauvegarder dans le fichier
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Synthèse Consolidée 🧠\n\n**Question :** {question}\n\n---\n\n")
            f.write(final_answer)
            
        return {
            "output_file": os.path.abspath(output_file),
            "sources_used": len(valid_answers),
            "web_sources": web_sources_count,
            "synthesizer": f"{synth_config.name} ({synth_config.model})",
            "synthesis": final_answer,
            "rag_sources": compare_result.get("sources", [])
        }
